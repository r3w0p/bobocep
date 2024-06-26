------------
Installation
------------

Dependencies
============

Python
------

:code:`BoboCEP` requires :code:`Python 3.9` or later.
If you are using `Raspberry Pi OS <https://www.raspberrypi.com/software/>`_,
it should come with this as standard.
You can check this using:

.. code:: console

    python --version

However, if a suitable version is not installed, then you will need to install
it yourself.
See `here <https://www.python.org/ftp/python/>`_ for available Python versions.
The following instructions will focus on :code:`Python 3.9.16`.

Download :code:`Python 3.9.16`, unpack it, and then enter the
directory containing its files.

.. code:: console

    wget https://www.python.org/ftp/python/3.9.16/Python-3.9.16.tar.xz
    tar -xf Python-3.9.16.tar.xz
    cd Python-3.9.16

Next, configure and install.

.. code:: console

    ./configure
    make -j 4
    sudo make altinstall

Finally, update :code:`pip` to the latest version.

.. code:: console

    python3.9 -m pip install --upgrade pip

Install via pip
===============

You can install the latest version of :code:`BoboCEP` via :code:`pip` with:

.. code:: console

    pip install BoboCEP


virtualenv
----------

If you would like to install :code:`BoboCEP` in a virtual environment,
consider using the following.

.. code:: console

    sudo apt install python3-virtualenv -y

    virtualenv venv
    source venv/bin/activate
    pip install BoboCEP
    deactivate


Build Manually
==============

You can also build :code:`BoboCEP` manually with:

.. code:: console

    git clone https://github.com/r3w0p/bobocep.git BoboCEP
    cd BoboCEP
    pip install .


Development
===========

If you want to develop :code:`BoboCEP`, see
`Developer Guide <developer_guide.html>`_
for more information.
