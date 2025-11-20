# Changelog

All notable changes made by us to the source code of the Anki-Connect project are documented below.

## Fixes
- CORS not working when allowing localhost unless the port is specified explicitly.

## Additions
- Return of **note modification time** in the `notesInfo` method
- Improved method `createModel` to set field descriptions and collapse status in the `inOrderFields` parameter
- New method: `notesModTime` that retrieves modification timestamps for notes
- New method: `isFsrsActive` that detects usage of FSRS for scheduling
- New method: `getVersion` that retrieves the Anki & Anki Connect Plus version in use
