CA resource plugin for OpenStack Heat
===========

Overview
--------
CA Plugin enables Server Cert generation from within Heat, to allow dynamic assigning of server Certificates.

Installation
------------

Heat plugins must reside in the `plugins_dir` directory defined in [the Heat Engine configuration file](https://wiki.openstack.org/wiki/Heat/Plugins#Installation_and_Configuration). By default, the directories `/usr/lib64/heat` and `/usr/lib/heat` are searched.

To install the CA resource plugin to an unmodified Heat installation using setuptools:

    sudo python setup.py install --install-purelib=/usr/lib/heat


Examples
--------

See the directory [examples/](examples/) for examples.
