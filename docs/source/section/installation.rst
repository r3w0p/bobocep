Installation
************

Requirements
============

The :code:`bobocep` software requires the following.

- **Python 3.7**.
  This is the only version of Python that :code:`bobocep` has currently been tested on.

- **Message Broker**.
  This is needed to network multiple software instances together in order to provide the active replication of
  partially-completed complex events.
  You can connect to any message broker that is compatible with the `AMQP 0-9-1 <https://www.amqp.org/>`_ protocol,
  such as `RabbitMQ <https://www.rabbitmq.com/>`_.
  This is only required if you want to distribute :code:`bobocep` across multiple devices.

You can install the latest version via :code:`pip` using the following command:

.. code:: console

    pip install bobocep


Walkthrough
===========

Raspberry Pi
------------

This section will guide you into setting up :code:`bobocep` on a Raspberry Pi.
It assumes you are using `Raspbian OS <https://www.raspberrypi.org/downloads/>`_ and that you will use RabbitMQ for
the message broker.

Dependencies
++++++++++++

To begin, we will update Raspbian and install all of the necessary dependencies.

.. code:: console

    sudo apt-get update -y
    sudo apt install build-essential wget erlang logrotate rabbitmq-server tk-dev libncurses5-dev \
        libncursesw5-dev libreadline6-dev libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev \
        libexpat1-dev liblzma-dev zlib1g-dev libffi-dev -y
    sudo apt-get -f install -y

Python 3.7
++++++++++

We will download Python 3.7.4, unpack it, then enter the newly created directory containing its files.

.. code:: console

    wget https://www.python.org/ftp/python/3.7.4/Python-3.7.4.tar.xz
    tar -xf Python-3.7.4.tar.xz
    cd Python-3.7.4

Next, we will configure and install Python.

.. code:: console

    ./configure
    make -j 4
    sudo make altinstall

Finally, we will update pip to the latest version.

.. code:: console

    python3.7 -m pip install --upgrade pip


RabbitMQ
++++++++

RabbitMQ and its dependencies have already been installed in previous steps.
We will now start the server.

.. code:: console

    service rabbitmq-server start

If you would like access to the `Management Plugin <https://www.rabbitmq.com/management.html>`_, you can install it
and configure a user account for it with administrator privileges, as follows.

.. code:: console

    rabbitmq-plugins enable rabbitmq_management
    rabbitmqctl add_user USERNAME PASSWORD
    rabbitmqctl set_user_tags USERNAME administrator
    rabbitmqctl set_permissions -p / USERNAME ".*" ".*" ".*"

.. note:: These instructions will probably give you an older version of RabbitMQ.
          If you require a later version, consider reading the RabbitMQ guides
          `here <https://www.rabbitmq.com/download.html>`_.


bobocep
+++++++

Finally, we will download :code:`bobocep` with the command shown above.

.. code:: console

    pip install bobocep

Once this is done, you can begin importing :code:`bobocep` into your own project.
