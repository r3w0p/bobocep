---------------
Developer Guide
---------------

Dependencies
============

You will need to install the core :code:`BoboCEP` requirements from both
:code:`requirements.txt` and its additional development requirements from
:code:`requirements-dev.txt`.
For example:

.. code:: console

    pip install -r requirements.txt
    pip install -r requirements-dev.txt


Development Tools
=================

:code:`BoboCEP` uses GitHub Actions for *Continuous Integration* (CI) and
*Continuous Deployment* (CD).
It uses two YAML scripts to trigger the respective action workflows, namely:

1. :code:`.github/workflows/cicd.yml` for CI/CD tasks, including:
   linting, type checking, code coverage, documentation coverage, and
   deployment to PyPI.
2. :code:`.github/workflows/security.yml` for security checks.

These scripts are triggered on a push to the :code:`main` branch.
The security script also runs periodically.

It is recommended that you run the individual CI/CD tasks manually before
committing.
These are discussed next.


Code Linting
------------

:code:`flake8` is used for code linting.
Run the following two commands to lint :code:`BoboCEP` and its test suite,
respectively.

.. code::

    flake8 ./bobocep --count --select=E9,F63,F7,F82 --show-source --statistics
    flake8 ./tests --count --select=E9,F63,F7,F82 --show-source --statistics


Code Testing and Coverage
-------------------------

:code:`coverage` is used for code testing and coverage.
Results are uploaded to
`Code Climate <https://codeclimate.com/github/r3w0p/bobocep/>`_.
Run the following command to test :code:`BoboCEP`.

.. code::

    coverage run -m pytest tests

The coverage configuration can be found in :code:`.coveragerc`.
GitHub Actions additionally enforces a minimum coverage of 100%.
You can check that this requirement has been satisfied using the following.

.. code::

    coverage report --fail-under=100

.. note::
    If you are unable to achieve 100% coverage with your code contribution,
    you can omit code from testing in :code:`.coveragerc`.

You can locally inspect the code coverage with an HTML output by running
the following.

.. code::

    coverage html


Documentation
-------------

Documentation is built using :code:`sphinx` and is deployed via
`Read the Docs <https://bobocep.readthedocs.io/en/latest/>`_.
You can compile documentation locally via the following.

.. code::

    cd docs
    make html

Or, for Windows (PowerShell).

.. code::

    cd docs
    .\make.bat html


Documentation Coverage
----------------------

:code:`interrogate` is used for testing and code coverage.
Run the following command to check :code:`BoboCEP` documentation coverage.
It requires a minimum documentation coverage of 100%.

.. code::

    interrogate -vv bobocep --fail-under 100


Type Checking
-------------

:code:`mypy` is used for type checking.
Run the following two commands to check :code:`BoboCEP` and its test suite,
respectively.

.. code::

    mypy ./bobocep
    mypy ./tests


Versioning
----------

:code:`BoboCEP` uses `Semantic Versioning <https://semver.org/>`_ and
the :code:`bump2version` tool for editing the software version.
See `here <https://pypi.org/project/bump2version/>`_ for more information.
The :code:`major`, :code:`minor`, or :code:`patch` components of the version
number can be changed with the following:

.. code::

    bump2version patch
