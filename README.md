# TODO

- Setup all log messages on all events, its missing some cases.
- Setup error handling in some cases.
- There's a bug when removing downloaded files and keeping control file. When checking if the file exists in the app's constructor somehow one file is not checked, if there was 3 files, only 2 gets noticed and removed entry.