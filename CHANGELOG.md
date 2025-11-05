# Changelog

All notable changes made by us to the source code of the Anki-Connect project are documented below.

## Fixes
- CORS not working when allowing localhost unless the port is specified explicitly.

## Additions
- Return of **note modification time** in the `notesInfo` method
- New method: `notesModTime` that retrieves modification timestamps for notes
- New method: `isFsrsActive` that detects usage of FSRS for scheduling
