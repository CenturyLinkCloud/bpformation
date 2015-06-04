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

```
> ./bpformation.py package -h
usage: bpformation.py package [-h]

                              {list,upload,publish,upload-and-publish,delete,download,execute}
                              ...

positional arguments:
  {list,upload,publish,upload-and-publish,delete,download,execute}
    list                List package inventory
    upload              Uploaded package to specified alias
    publish             Uploaded packages to specified alias
    upload-and-publish  Uploaded then publish packages to specified alias
    delete              Delete published package
    download            Download published package
    execute             Execute package

optional arguments:
  -h, --help            show this help message and exit
```


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
> ./bpformation.py package upload --file /tmp/test_package_1.zip
✔  test_package_1.zip successfully uploaded (0 seconds)

# Upload all zip files in a directory
> ./bpformation.py package upload --file /tmp/*.zip
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
> ./bpformation.py package upload-and-publish -h
usage: bpformation.py package upload-and-publish [-h] --file [FILE [FILE ...]]
                                                 --type {Windows,Linux}
                                                 --visibility
                                                 {Public,Private,Shared} --os
                                                 [OS [OS ...]]

optional arguments:
  -h, --help            show this help message and exit
  --file [FILE [FILE ...]]
                        Files to process
  --type {Windows,Linux}
                        Operating system
  --visibility {Public,Private,Shared}
                        Package visibility
  --os [OS [OS ...]]    Operating system list (regex supported)
```

Example:

```
> ./bpformation.py package upload-and-publish --file /tmp/test_package_1.zip --type Linux --visibility Private --os Ubuntu
✔  test_package_1.zip successfully uploaded (0 seconds)
✔  test_package_1.zip publish job submitted
✔  test_package_1.zip publish job complete (60 seconds)
```

### Package Delete

Deletes one or more existing packages owned by your account.  Packages are keyed by UUID which can be found either from the [package list](#packagelist) command, inside the manifest file itself if you've still got it, or by viewing the URL from the control portal when viewing package details.

```
> ./bpformation.py package delete -h
usage: bpformation.py package delete [-h] --uuid [UUID [UUID ...]]

optional arguments:
  -h, --help            show this help message and exit
  --uuid [UUID [UUID ...]]
                        UUID for packages
```

Example:

```
# Delete Some of those Test Packages
> ./bpformation.py package delete --uuid 6b67648d-71fe-4501-8d4d-15cd496336da \
                                         7a5c86ce-1140-4d4f-bbd0-5b2859a79451 \
                                         75eb2d6c-253b-448c-ada4-a6ad57598576 
✔  6b67648d-71fe-4501-8d4d-15cd496336da package deleted
✔  7a5c86ce-1140-4d4f-bbd0-5b2859a79451 package deleted
✔  75eb2d6c-253b-448c-ada4-a6ad57598576 package deleted
```

### Package Download

Download a zip file of one or more packages specified by UUID.  The package must be visible to your account but need not be owned by you.
The downloaded package will be saved in your current directory with the name `uuid`.zip

```
> ./bpformation.py package download --help
usage: bpformation.py package download [-h] --uuid [UUID [UUID ...]]

optional arguments:
  -h, --help            show this help message and exit
  --uuid [UUID [UUID ...]]
                        UUID for packages
```

Example:

```
# Download package
> ./bpformation.py package download --uuid 3819ee8d-c276-4d11-9d57-146fd9937a38
✔  3819ee8d-c276-4d11-9d57-146fd9937a38 package downloaded
> ls -l 3819ee8d-c276-4d11-9d57-146fd9937a38.zip
-rw-r--r--  1 user  staff   1.2K Jun  4 15:34 3819ee8d-c276-4d11-9d57-146fd9937a38.zip
```


### Package Execute

Execute a single package on one or more existing servers.  If any `global` or `deploy`-time parameters are required specify them in `key`=`value` pairs.

```
> ./bpformation.py package execute -h
usage: bpformation.py package execute [-h] --uuid UUID --server
                                      [SERVER [SERVER ...]]
                                      [--parameter [PARAMETER [PARAMETER ...]]]

optional arguments:
  -h, --help            show this help message and exit
  --uuid UUID           UUID for package
  --server [SERVER [SERVER ...]]
                        Servers targets for package execution
  --parameter [PARAMETER [PARAMETER ...]]
                        key=value pairs for package parameters
```

Example:

```
# Execute the Linux Update patching package on a few of my servers
> ./bpformation.py package execute --uuid 77ab3844-579d-4c8d-8955-c69a94a2ba1a --server CA1KRAPX04 CA1KRAPX05 CA1KRAPX06
✔  Execution request submitted for ca1krapx05
✔  Execution request submitted for ca1krapx06
✔  Execution request submitted for ca1krapx07
✔  Execution completed on ca1krapx05, ca1krapx06, ca1krapx04 (287 seconds)
```




## Blueprints

A CenturyLink Cloud Blueprint package is an invoked piece of software, uploaded to the cloud platform, which customizes a server template.  [Learn the difference between templates, blueprints and packages](https://www.centurylinkcloud.com/knowledge-base/blueprints/understanding-the-difference-between-templates-blueprints-and-packages/)

One challenge to keep in mind with managing Blueprints using the `bpformation` toolset is that Blueprints don't actually key on a globaly unique ID.  Keep this in mind when searching for the ID associated with a Blueprint - we always use the Blueprints ID associated with your *primary datacenter*.  To make this easier for you we always include the ID when performing an [export](#blueprintexport) allowing you to re-use all identifying information for subsequent `bpformation` invocations.

```
> ./bpformation.py blueprint -h
usage: bpformation.py blueprint [-h]
                                {list,export,import,update,delete,execute} ...

positional arguments:
  {list,export,import,update,delete,execute}
    list                List blueprint inventory
    export              Export blueprint
    import              Import blueprint from json
    update              Update existing blueprint from json
    delete              Delete blueprint
    execute             Execute blueprint

optional arguments:
  -h, --help            show this help message and exit
```

### Blueprint List

Query all Blueprints visible to your account, optionally filtering by any piece of metadata that's displayed. 

```
> ./bpformation.py blueprint list -h
usage: bpformation.py blueprint list [-h] [--filter [FILTER [FILTER ...]]]

optional arguments:
  -h, --help            show this help message and exit
  --filter [FILTER [FILTER ...]]
                        Regex filter Results by name, author, status, visibility (and)
```

Example:

```
# Find Private-Shared blueprints in my account
> ./bpformation.py blueprint list --filter privateshared
+--------------------------------------+------+---------------+--------------+
| name                                 | id   | visibility    | date_added   |
+--------------------------------------+------+---------------+--------------+
| CaaS                                 | 152  | privateshared | Mar 04, 2013 |
| Exchange 2010 with Domain Controller | 627  | privateshared | Jul 06, 2013 |
| Linux App Stack Demo                 | 719  | privateshared | Jan 20, 2014 |
| Public IP Test                       | 2033 | privateshared | Dec 15, 2014 |
| Small SharePoint Farm                | 585  | privateshared | Jul 06, 2013 |
+--------------------------------------+------+---------------+--------------+

# Find SQL Server blueprints
> ./bpformation.py blueprint list --filter sql
+---------------------------------------+------+------------+--------------+
| name                                  | id   | visibility | date_added   |
+---------------------------------------+------+------------+--------------+
| Install SQL 2012 RC0 Standard         | 424  | public     | Mar 06, 2012 |
| Install SQL Server on Existing Server | 47   | public     | Oct 22, 2012 |
| Install SQL Server on New Server      | 46   | public     | Oct 22, 2012 |
+---------------------------------------+------+------------+--------------+
```


### Blueprint Export

Export existing Blueprints you have access to from your account into an easy to modify and maintain [json](http://json.org/) file.
This can serve as the basis for extending a Blueprint from someone else, maintaining a Blueprint originally designed from within the CenturyLink 
Cloud control portal, or managing the lifecycle of a Blueprint as part of a version control system.

The default naming for these downloaded files is composed of `blueprint name`-`id`-`version`.json.

Exports keep all IDs and task sequencing intact to subsequent [imports](#blueprintimport) and [updates)(#blueprintupdate) work as expected.
An export json contains `metadata`, `tasks`, and a template `execute` section for re-use across other `bpformation` functions.  
View an [example blueprint json](#) file for a look at the major sections and their respective roles.

```
> ./bpformation.py blueprint export -h
usage: bpformation.py blueprint export [-h] --id ID [--file FILE]

optional arguments:
  -h, --help   show this help message and exit
  --id ID      Blueprint ID (note this ID is not globally unique - find this
               from your primary datacenter
  --file FILE  Filename target for Blueprint json definition
```

Example:

```
# Export Blueprint using default naming
> ./bpformation.py blueprint export --id 2668
✔  Pivotal GemFire v0.1 exported to pivotal_gemfire-2668-0.1.json (1 tasks)
> ls -l pivotal_gemfire-2668-0.1.json
-rw-r--r--  1 owner  staff   698B Jun  4 16:09 pivotal_gemfire-2668-0.1.json

# Export Blueprint using custom file naming
> ./bpformation.py blueprint export --id 2668 --file my_gemfire.json
✔  Pivotal GemFire v0.1 exported to my_gemfire.json (1 tasks)

# Export Blueprint to stdout
> ./bpformation.py blueprint export --id 3526 --file -
{
    "execute": {
    },
    "metadata": {
        "description": "x",
        "name": "Testdeploy",
        "owner": "owner@ctl.io",
        "version": "0.2",
        "visibility": "private"
    },
    "tasks": [
        {
            "cpu": "1",
            "description": "x",
            "id": "1adcbabb-fa80-4385-a83c-43ebd05d5e42",
            "name": "X",
            "ram": "1",
            "tasks": [
                {
                    "id": "c189a7fc-2e9c-4fed-a59b-2d68fa77bdae",
                    "name": "Linux Update",
                    "type": "package",
                    "uuid": "77ab3844-579d-4c8d-8955-c69a94a2ba1a"
                }
            ],
            "template": "CENTOS-6-64-TEMPLATE",
            "type": "server",
            "uuid": "cb9762b3-61a6-4cfb-af97-96bf7dbfc359"
        }
    ]
}
```



### Blueprint Import

Import a new Blueprint into CenturyLink Cloud.  Source must be a json file but can come from another exported Blueprint (we strip
all unique IDs if they exist) or from a hand-crafted definition.  

The `metadata` and `tasks` sections must be populated for a successful import.  View an [example blueprint json](#) file for a 
look at the major sections and their respective roles.

```
> ./bpformation.py blueprint import -h
usage: bpformation.py blueprint import [-h] --file [FILE [FILE ...]]

optional arguments:
  -h, --help            show this help message and exit
  --file [FILE [FILE ...]]
                        Blueprint definition json files
```

Example:

```
# Import test Blueprint
> ./bpformation.py blueprint import --file testdeploy.json
✔  Testdeploy v0.2 imported ID 3526 (1 tasks)

```


### Blueprint Update

Update an existing Blueprint my applying a modified json definition.  Updates may take several minutes to replicate and reach global consistency.

```
```

Example:

```
# Update modified test Blueprint
> perl -p -i -e 's/"version": "[0-9\.]+"/"version": "1.0"/' testdeploy-3526-0.2.json
> ./bpformation.py blueprint update --file testdeploy-3526-0.2.json
✔  Testdeploy v1.0 updated ID 3526 (1 tasks)
```


### Blueprint Delete

Delete one or more Blueprints owned by your account.  Deletion may take several minute to replicate globally.

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


