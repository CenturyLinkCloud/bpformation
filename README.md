# CenturyLink Cloud Blurpint Formation CLI Tool (bp-formation)

This repository contains a command line interface *CLI* to interact with the *[CenturyLink Cloud](http://www.centurylinkcloud.com)* Blueprints packaging and workflow services,.  

## Contents

* [Installing](#installing)
* [Examples](#examples)
* [Usage](#usage)
* Python SDK (documentation coming soon)


## Installing

### Via Python's pip
Cross-platform installation is available via pypi.  Requires *Python 2.7* - this is not currently compatible with Python 3.
If you have pip already installed the following command will get you running:
```
> pip install bpformation
```

This should automatically install the following dependencies used by the CLI: prettytable, clint, argparse, requests, [clc-sdk](https://github.com/CenturyLinkCloud/clc-python-sdk)

If you do not have pip (the Python package manager) installed a quickstart install of this prereq on Linux/Mac is:
```
> curl https://bootstrap.pypa.io/get-pip.py | sudo python
```

### Windows pre-packaged executable
The CLI is available as a prepackaged single-file Windows executable and the most recent compiled version is always available [here](https://github.com/CenturyLinkCloud/bp-foration/raw/master/src/dist/bpformation.exe).


## Examples



## Usage

```
> ./bpformation.py
usage: bpformation.py [-h] [--config CONFIG] [--alias ALIAS]
                      [--control-user USER] [--control-password PASS]
                      [--quiet] [--verbose] [--cols [COL [COL ...]]]
                      [--format {json,table,text,csv}]
                      {package,blueprint} ...
```


### Global Parameters and General Usage

```
> ./bpformation.py -h
usage: bpformation.py [-h] [--config CONFIG] [--alias ALIAS]
                      [--control-user USER] [--control-password PASS]
                      [--quiet] [--verbose] [--cols [COL [COL ...]]]
                      [--format {json,table,text,csv}]
                      {package,blueprint} ...

CLI tool for interacting with CenturyLink Blueprints Package and Workflow
Services. http://www.CenturyLinkCloud.com

optional arguments:
  -h, --help            show this help message and exit
  --config CONFIG, -c CONFIG
                        Ini config file
  --alias ALIAS, -a ALIAS
                        Operate on specific account alias
  --control-user USER   Control username
  --control-password PASS
                        Control password
  --quiet, -q           Supress status output (repeat up to 2 times)
  --verbose, -v         Increase verbosity
  --cols [COL [COL ...]]
                        Include only specific columns in the output
  --format {json,table,text,csv}, -f {json,table,text,csv}
                        Output result format (table is default)

Commands:
  {package,blueprint}
    package             Package level activities (list, package, upload,
                        publish, etc.)
    blueprint           Blueprint level activities (list, import, export,
                        delete, etc.)
```


### Authentication
All commands require authentication which can be accomplished in several ways in increasing order of priority.
* System configuration file at `/usr/local/etc/bpformation_config` (POSIX) or `%PROGRAMDATA%\bpformation\bpformation.ini` (Windows)
* User specific configuration file at `~/.bpformation` (POSIX) or `.\bpformation.ini` (Windows)
* Specify configuration file with --config / -c command line option
* Define environment variables (CONTROL_USER / CONTROL_PASSWORD)
* Pass credentials as command line options

Configuration files follow ini syntax.  Reference the [example.ini](src/example_config.ini) file with all currently accepted fields.


