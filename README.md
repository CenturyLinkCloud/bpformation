# CenturyLink Cloud Blurpint Formation CLI Tool (bp-formation)

This repository contains a command line interface *CLI* to interact with the *[CenturyLink Cloud](http://www.centurylinkcloud.com)* Blueprints packaging and workflow services,.  

## Contents

* [Installing](#installing)
* [Examples](#examples)
* [Usage](#usage)
 * [Packages](#packages) - [List](#packagelist), [Upload](#packageupload), [Publish](#packagepublish), [Upload and Publish](#packageuploadandpublish), [Delete](#packagedelete), [Download](#packagedownload), [Execute](#packageexecute)
 * [Blueprints](#blueprints) - [List](#blueprintlist), [Export](#blueprintexport), [Import](#blueprintimport), [Update](#blueprintupdate), [Delete](#blueprintdelete), [Execute](#blueprintexecute)
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

### Publish, Upload, and Test Blueprint Package on an Existing  Server


### Replicate a Public Blueprint, Customize, Republish, then Deploy


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
    package             Package level activities (list, package, upload, publish, etc.)
    blueprint           Blueprint level activities (list, import, export, delete, etc.)
```


### Authentication
All commands require authentication which can be accomplished in several ways in increasing order of priority.
* System configuration file at `/usr/local/etc/bpformation_config` (POSIX) or `%PROGRAMDATA%\bpformation\bpformation.ini` (Windows)
* User specific configuration file at `~/.bpformation` (POSIX) or `.\bpformation.ini` (Windows)
* Specify configuration file with --config / -c command line option
* Define environment variables (CONTROL_USER / CONTROL_PASSWORD)
* Pass credentials as command line options

Configuration files follow ini syntax.  Reference the [example.ini](src/example_config.ini) file with all currently accepted fields.



## Packages

A CenturyLink Cloud Blueprint package is an invoked piece of software, uploaded to the cloud platform, which customizes a server template.  [Learn the difference between templates, blueprints and packages](https://www.centurylinkcloud.com/knowledge-base/blueprints/understanding-the-difference-between-templates-blueprints-and-packages/).


### Package List

Query all packages visible to your account, optionally filtering by any piece of metadata that's displayed. 

```
> ./bpformation.py package list --help
usage: bpformation.py package list [-h] [--filter [FILTER [FILTER ...]]]

optional arguments:
  -h, --help            show this help message and exit
    --filter [FILTER [FILTER ...]]
	                        Regex filter Results by name, author, status, visibility (and)
```

Example:

```
# Show all public packages for Linux tagged with Security
> ./bpformation.py package list --filter public linux security
+-----------------------------------------------------------------------+--------------------------------------+----------+------------+-----------+
| name                                                                  | uuid                                 | owner    | visibility | status    |
+-----------------------------------------------------------------------+--------------------------------------+----------+------------+-----------+
| Install Vormetric Data Security Transparent Encryption Agent on Linux | e0e03253-ec7c-4278-b6c4-4ca0b5244b38 | cgosalia | Public     | published |
| Security - Install OSSEC Agent for Linux                              | 407a3b17-cf33-4e00-84ba-9c187cdf69d6 | eco.team | Public     | published |
| Security - Install OSSEC Manager for Linux                            | fec41e23-0f10-4b54-9fe7-5011b1229764 | eco.team | Public     | published |
+-----------------------------------------------------------------------+--------------------------------------+----------+------------+-----------+

# Find my private test packages - need to clean these up sometime soon
> ./bpformation.py package list --filter private test
+-------------------+--------------------------------------+--------+------------+-----------+
| name              | uuid                                 | owner  | visibility | status    |
+-------------------+--------------------------------------+--------+------------+-----------+
| Test defaults     | 6b67648d-71fe-4501-8d4d-15cd496336da | owner  | Private    | published |
| Test global       | 7a5c86ce-1140-4d4f-bbd0-5b2859a79451 | owner  | Private    | published |
| Test parameter    | 75eb2d6c-253b-448c-ada4-a6ad57598576 | owner  | Private    | published |
| test default2     | fd19358e-f43f-4aaf-8622-2cb222500ffa | owner  | Private    | published |
| test system parms | 3819ee8d-c276-4d11-9d57-146fd9937a38 | owner  | Private    | published |
+-------------------+--------------------------------------+--------+------------+-----------+
```

### Package Upload

Upload one or more Blueprint packages into your account.  This call obtains the FTP endpoint used by your account then uploads the package via ftp.
This can be used both for new packages and for updating the contents of an existing package.  Source file must be a valid  [Blueprint Package](https://www.centurylinkcloud.com/knowledge-base/blueprints/blueprint-package-manifest-builder-wizard/) which is a zip file that contains a valid XML `package.manifest` and optionally any supporting scripts or binaries.

```
> ./bpformation.py package upload -h
usage: bpformation.py package upload [-h] --file [FILE [FILE ...]]

optional arguments:
  -h, --help            show this help message and exit
    --file [FILE [FILE ...]]
	                        Files to upload
```

Example:

```
# Upload package zip file
> ./bpformation.py package upload --file test_package_1.zip
✔  test_package_1.zip successfully uploaded (0 seconds)

# Upload all zip files in a directory
> ./bpformation.py package upload --file *.zip
✔  test_package_1.zip successfully uploaded (0 seconds)
✔  test_package_2.zip successfully uploaded (0 seconds)
✔  test_package_3.zip successfully uploaded (0 seconds)

```


### Package Publish

Publish one or more already uploaded packages into your account.  This can be either a new package or can be an update to an existing package.  Note that the package UUID must be globally unique and can never be reused, so if you delete a package and want to re-add it or if you have a dev and prod release of the package they will need distinct UUIDs.
Provide the OS `type` classification (`Linux` or `Windows), one or more regexs of `os`, visibility (Private, Shared, Public), and the name of all `file` already resident on the FTP server.

```
> ./bpformation.py package publish --help
usage: bpformation.py package publish [-h] --file [FILE [FILE ...]] --type
                                      {Windows,Linux} --visibility
                                      {Public,Private,Shared} --os
                                      [OS [OS ...]]

optional arguments:
  -h, --help            show this help message and exit
  --file [FILE [FILE ...]]
                        Uploaded filename to process
  --type {Windows,Linux}
                        Operating system
  --visibility {Public,Private,Shared}
                        Package visibility
  --os [OS [OS ...]]    Operating system list (regex supported)
```

Example:

```
# Publish already uploaded package
> ./bpformation.py package publish --file test_package_1.zip --type Linux --visibility Private --os Ubuntu
✔  test_package_1.zip publish job submitted
✔  test_package_1.zip publish job complete (13 seconds)
```

### Package Upload and Publish

Combine the package [Upload](#packageupload) and [Publish](#packagepublish) steps into one.

```
```

Example:

```
```

### Package Delete

lorem ipsum 

```
```

Example:

```
```

### Package Download

lorem ipsum 

```
```

Example:

```
```



### Package Execute

lorem ipsum 

```
```

Example:

```
```




## Blueprints

A CenturyLink Cloud Blueprint package is an invoked piece of software, uploaded to the cloud platform, which customizes a server template.  [Learn the difference between templates, blueprints and packages](https://www.centurylinkcloud.com/knowledge-base/blueprints/understanding-the-difference-between-templates-blueprints-and-packages/)


### Blueprint List

lorem ipsum 

```
```

Example:

```
```



### Blueprint Export

lorem ipsum 

```
```

Example:

```
```



### Blueprint Import

lorem ipsum 

```
```

Example:

```
```



### Blueprint Update

lorem ipsum 

```
```

Example:

```
```



### Blueprint Delete

lorem ipsum 

```
```

Example:

```
```

### Blueprint Execute

lorem ipsum 

```
```

Example:

```
```


