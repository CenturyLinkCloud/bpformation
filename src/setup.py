
#
# python setup.py sdist
# python setup.py bdist_dumb
# python setup.py bdist_rpm
#

from setuptools import setup, find_packages

setup(
	name = "bpformation",
	version = "0.1",
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

