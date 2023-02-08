Installation
************

Instructions
============

Install via pip
---------------

You can install the latest version via :code:`pip` using the following command.

.. code:: console

    pip install BoboCEP


Build Manually
--------------

You can also build :code:`BoboCEP` manually, as follows.

.. code:: console

    git clone https://github.com/r3w0p/bobocep.git BoboCEP
    cd BoboCEP
    pip install .


Raspberry Pi
============

This section will guide you into setting up :code:`BoboCEP` on a Raspberry Pi.
For this walkthrough, we will assume that you are using
`Raspberry Pi OS <https://www.raspberrypi.com/software/>`_.

Dependencies
------------

To begin, we will update Raspbian and install all of the necessary dependencies.

TODO change apt install below

.. code:: console

    sudo apt-get update -y
    sudo apt install build-essential wget erlang logrotate rabbitmq-server tk-dev libncurses5-dev \
        libncursesw5-dev libreadline6-dev libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev \
        libexpat1-dev liblzma-dev zlib1g-dev libffi-dev -y
    sudo apt-get -f install -y

Python
------

:code:`BoboCEP` requires :code:`Python 3.9` or later.
Raspberry Pi OS should come with this as standard, and you can check using:

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

Update :code:`pip` to the latest version.

.. code:: console

    python3.9 -m pip install --upgrade pip


Once this is done, follow :ref:`installation:Instructions` above.
