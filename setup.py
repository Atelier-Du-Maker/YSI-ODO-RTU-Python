#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

import ODO_sensor_lib


setup(

	name='ODO_sensor_lib',

	# la version du code
	version=ODO_sensor_lib.__version__,
	packages=find_packages(),
	author="Mickaël Veleine",
	author_email="mickael@atelierdumaker.com",
	description="Lib to use YSI ODO RTU sensor with Python",
	long_description_content_type='text/markdown',
	long_description=open('README.md').read(),
	install_requires= ["pymodbus, pyserial"],
	include_package_data=True,
	url='https://github.com/Atelier-Du-Maker/YSI-ODO-RTU-Python',
	classifiers=[
		"Programming Language :: Python",
		"Development Status :: 2 - Pre-Alpha",
		"License :: OSI Approved :: MIT License",
		"Natural Language :: English",
		"Operating System :: OS Independent",
		"Programming Language :: Python",
		"Topic :: System :: Hardware :: Hardware Drivers",
	],


)
