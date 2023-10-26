# ouioui

Small utility script and library to download the IEEE OUI MA-L assignments file, override them if needed, and save them into a SQLite db to query.

## requirements

* python >= 3.12
* peewee >= 3.17.0
* requests >= 2.31.0

## usage

* in addition, the tests folder has examples for library usage.

```plain
usage: ouioui.py [-h] [--debug] [-c FILE] (-q QUERY | --update | --package_for_kismet)

small utility script, and library, to download the IEEE OUI MA-L assignments file, override them if needed, and save them into a SQLite db to query.

options:
  -h, --help            show this help message and exit
  --debug               increase verbosity with debug messages
  -c FILE, --config FILE
                        configuration file to override default settings

actions:
  one of these is required

  -q QUERY, --query QUERY
                        OUI prefix to look up (charset: A-Z0-9, others will be removed)
  --update              fetch sources, load custom oui, rebuild database
  --package_for_kismet  fetch sources, package as .txt.gz for kismet (ouifile=<path> in kismet_site.conf)

version 2023.10dev1```
