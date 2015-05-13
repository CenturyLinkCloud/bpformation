# CenturyLink Cloud Blurpint Formation CLI Tool (bp-formation)

This repository contains a command line interface *CLI* to interact with the *[CenturyLink Cloud](http://www.centurylinkcloud.com)* Blueprints packaging and workflow services,.  

## Contents

* [Installing](#installing)
* [Examples](#examples)
* [Usage](#usage)


## Installing

### Via Python's pip
Cross-platform installation is available via pypi.  Requires *Python 2.7* - this is not currently compatible with Python 3.
If you have pip already installed the following command will get you running:
```
> pip install bp-formation
```

This should automatically install the following dependencies used by the CLI: prettytable, clint, argparse, requests

If you do not have pip (the Python package manager) installed a quickstart install of this prereq on Linux/Mac is:
```
> curl https://bootstrap.pypa.io/get-pip.py | sudo python
```

### Windows pre-packaged executable
The CLI is available as a prepackaged single-file Windows executable and the most recent compiled version is always available [here](https://github.com/CenturyLinkCloud/bp-foration/raw/master/src/dist/bp-formation.exe).


