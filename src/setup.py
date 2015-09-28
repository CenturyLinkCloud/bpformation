
VERSION = "0.20"

#
# python setup.py sdist
# python setup.py bdist_dumb
# python setup.py bdist_rpm
#

import subprocess
from setuptools import setup, find_packages

# Apply version
subprocess.Popen(["/usr/bin/perl","-p","-i","-e","s/^__version__.*/__version__ = \"%s\"/" % VERSION,"bpformation/__init__.py"]).wait()


# Setup
setup(
	name = "bpformation",
	version = VERSION,
	packages = find_packages("."),

	install_requires = ['prettytable','clint','argparse','requests','lxml','clc-sdk'],

	entry_points = {
		'console_scripts': [
			'bpformation  = bpformation.cli:main',
		],
	},


	# metadata for upload to PyPI
	author = "Keith Resar",
	author_email = "Keith.Resar@CenturyLinkCloud.com",
	description = "Blueprint Formation CLI",
	keywords = "CenturyLink Cloud Blueprint CLI",
	url = "https://github.com/CenturyLinkCloud/bp-formation",

	# could also include long_description, download_url, classifiers, etc.
)

