tdirstat
========

Terminal-based directory statistics with a nice TUI and quick actionable information

**Overview**

This project is inspired by projects such as kdirstat and qdirstat.
Easily find where your disk space has gone, without waiting for a full-drive scan
to complete. 

Contributions welcome!

**Installation**

.. code::

    pip install --user setuptools tdirstat@git+https://github.com/apockill/tdirstat



Then, to run:
.. code::

    tdirstat /


The first argument is the directory you wish to map. By default, it picks the current working directory. 

**Repository goals**

- Reduce memory usage
- Speed up scan time
- Add tooling for file and directory deletion
