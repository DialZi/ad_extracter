# AD extracter

## About

Extract AD to csv.
See `ATTRIBUTES`, `SEARCHED_FILTERS` and `HIGHLIGHT_GROUPS` for configuration.

## Features

For `memberOf` and `distinguishedName` you can highlight groups like as seperate column with **True** (Found) or **False**(Not found). 

P.S. It works for `CN` and `OU`. See code :) 

## Format `.env`

```
AD_USERNAME=admin
AD_DOMAIN=domain
AD_PASSWORD=super_pass
AD_HOST=1.1.1.1
AD_PORT=01
AD_SEARCH=DC=lol,DC=kek
```