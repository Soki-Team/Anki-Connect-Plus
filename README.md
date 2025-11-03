<p>
  <a href="https://soki.ai/projects/anki-connect-plus">
    <img src="./assets/ankiConnectPlus.svg" alt="Anki Connect Plus Logo" width="200">
  </a>
</p>

# Anki Connect Plus (ACP)
Fork of [Anki-Connect](https://git.sr.ht/~foosoft/anki-connect) with additional features to facilitate syncing with other projects like our Flashcard Maker for Anki (FMA).
Everything that can be done in Anki Connect can also be done with Anki Connect Plus, keeping compatibility with other addons relying on it.

Find a full list all modifications in the **[changelog](./CHANGELOG.md)**

Anki Connect Plus is compatible with the latest stable (2.1.x) releases of Anki; older versions (2.0.x and below) are no longer supported.

## Documentation
See the list of **[supported actions](./SUPPORTED_ACTIONS.md)**

## Installation

Until the add-on is officially deployed, Anki requires a **manual installation**.  
Follow these steps to add **ACP** to Anki:

1. **Zip the plugin contents**  
   - Go inside the plugin folder.  
   - Select all the files and folders inside it.  
   - Create a `.zip` archive from these items.  
   ⚠️ *Important:* Do **not** zip the plugin folder itself — only its contents.  

2. **Rename the archive**  
   Change the file name and extension to: ACFS.ankiaddon

3. **Install the add-on in Anki**  
- Open Anki.  
- Go to **Tools > Add-ons**.  (ctrs+shift+A for windows) 
- Click **Install from file...** and select/drag the `ACFS.ankiaddon` file.  

4. **Restart Anki**  
Close and reopen Anki to activate the add-on.
 
Anki must be kept running in the background in order for other applications to be able to use Anki Connect Plus. You can verify that Anki Connect Plus is running at any time by accessing `localhost:8765` in your browser. If the server is running, you will see the message `Anki Connect Plus` displayed in your browser window.

### Notes for Windows Users

Windows users may see a firewall nag dialog box appear on Anki startup. This occurs because Anki Connect Plus runs a local HTTP server in order to enable other applications to connect to it. The host application, Anki, must be unblocked for this plugin to function correctly.

### Notes for MacOS Users

Starting with [Mac OS X Mavericks](https://en.wikipedia.org/wiki/OS_X_Mavericks), a feature named *App Nap* has been introduced to the operating system. This feature causes certain applications which are open (but not visible) to be placed in a suspended state. As this behavior causes Anki Connect Plus to stop working while you have another window in the foreground, App Nap should be disabled for Anki:

1.  Start the Terminal application.
2.  Execute the following commands in the terminal window:
    ```bash
    defaults write net.ankiweb.dtop NSAppSleepDisabled -bool true
    defaults write net.ichi2.anki NSAppSleepDisabled -bool true
    defaults write org.qt-project.Qt.QtWebEngineCore NSAppSleepDisabled -bool true
    ```
3.  Restart Anki.

## Application Interface for Developers

Anki Connect Plus exposes internal Anki features to external applications via an easy to use API. After being installed, this plugin will start an HTTP server on port 8765 whenever Anki is launched. Other applications (including browser extensions) can then communicate with it via HTTP requests.

By default, Anki Connect Plus will only bind the HTTP server to the `127.0.0.1` IP address, so that you will only be able to access it from the same host on which it is running. If you need to access it over a network, you can change the binding address in the configuration. Go to Tools->Add-ons->Anki Connect Plus->Config and change the "webBindAddress" value. For example, you can set it to `0.0.0.0` in order to bind it to all network interfaces on your host. This also requires a restart for Anki.

### Sample Invocation

Every request consists of a JSON-encoded object containing an `action`, a `version`, contextual `params`, and a `key`
value used for authentication (which is optional and can be omitted by default). Anki Connect Plus will respond with an
object containing two fields: `result` and `error`. The `result` field contains the return value of the executed API,
and the `error` field is a description of any exception thrown during API execution (the value `null` is used if
execution completed successfully).

*Sample successful response*:
```json
{"result": ["Default", "Filtered Deck 1"], "error": null}
```

*Samples of failed responses*:
```json
{"result": null, "error": "unsupported action"}
```
```json
{"result": null, "error": "guiBrowse() got an unexpected keyword argument 'foobar'"}
```

For compatibility with clients designed to work with older versions of Anki Connect Plus, failing to provide a `version`
field in the request will make the version default to 4. Furthermore, when the provided version is level 4 or below, the
API response will only contain the value of the `result`; no `error` field is available for error handling.

You can use whatever language or tool you like to issue request to Anki Connect Plus, but a couple of simple examples are
included below as reference.

#### Curl

```bash
curl localhost:8765 -X POST -d '{"action": "deckNames", "version": 6}'
```

#### Powershell

```powershell
(Invoke-RestMethod -Uri http://localhost:8765 -Method Post -Body '{"action": "deckNames", "version": 6}').result
```

#### Python

```python
import json
import urllib.request

def request(action, **params):
    return {'action': action, 'params': params, 'version': 6}

def invoke(action, **params):
    requestJson = json.dumps(request(action, **params)).encode('utf-8')
    response = json.load(urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:8765', requestJson)))
    if len(response) != 2:
        raise Exception('response has an unexpected number of fields')
    if 'error' not in response:
        raise Exception('response is missing required error field')
    if 'result' not in response:
        raise Exception('response is missing required result field')
    if response['error'] is not None:
        raise Exception(response['error'])
    return response['result']

invoke('createDeck', deck='test1')
result = invoke('deckNames')
print('got list of decks: {}'.format(result))
```

#### JavaScript

```javascript
function invoke(action, version, params={}) {
    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        xhr.addEventListener('error', () => reject('failed to issue request'));
        xhr.addEventListener('load', () => {
            try {
                const response = JSON.parse(xhr.responseText);
                if (Object.getOwnPropertyNames(response).length != 2) {
                    throw 'response has an unexpected number of fields';
                }
                if (!response.hasOwnProperty('error')) {
                    throw 'response is missing required error field';
                }
                if (!response.hasOwnProperty('result')) {
                    throw 'response is missing required result field';
                }
                if (response.error) {
                    throw response.error;
                }
                resolve(response.result);
            } catch (e) {
                reject(e);
            }
        });

        xhr.open('POST', 'http://127.0.0.1:8765');
        xhr.send(JSON.stringify({action, version, params}));
    });
}

await invoke('createDeck', 6, {deck: 'test1'});
const result = await invoke('deckNames', 6);
console.log(`got list of decks: ${result}`);
```

### Authentication

Anki Connect Plus supports requiring authentication in order to make API requests.
This support is *disabled* by default, but can be enabled by setting the `apiKey` field of Anki-Config's settings (Tools->Add-ons->Anki Connect Plus->Config) to a desired string.
If you have done so, you should see the [`requestPermission`](#requestpermission) API request return `true` for `requireApiKey`.
You then must include an additional parameter called `key` in any further API request bodies, whose value must match the configured API key.
