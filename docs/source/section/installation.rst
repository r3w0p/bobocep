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

You can download the latest version via :code:`pip` using the following command:

.. code:: console

    pip install bobocep


Walkthrough
===========

Raspberry Pi
------------

This section will guide you into setting up :code:`bobocep` on a Raspberry Pi.
It assumes you are using `Raspbian OS <https://www.raspberrypi.org/downloads/>`_ and that you will use RabbitMQ for
the message broker.

Init
++++

To begin, we will update Raspbian and install some necessary programs.

.. code:: console

    sudo apt-get update -y
    sudo apt install wget -y


Python 3.7
++++++++++

@@@
@@@
    TODO make sure these steps are correct before committing.
@@@
@@@

Next we need to download Python 3.7.
We will download the file for Python 3.7.3.

.. code:: console

    wget https://www.python.org/ftp/python/3.7.3/Python-3.7.3.tar.xz
    tar -xf Python-3.7.3.tar.xz

.. code:: console

    cd Python-3.7.3
    sh ./configure --enable-optimizations
    make
    make altinstall

Finally, we will update pip.

.. code:: console

    python3.7 -m pip install --upgrade pip



RabbitMQ
++++++++




.. note:: These instructions will probably give you an older version of RabbitMQ.
          If you require a modern version, consider reading the RabbitMQ guides
          `here <https://www.rabbitmq.com/download.html>`_.


bobocep
+++++++

Finally, we will download :code:`bobocep` with the command shown above.

.. code:: console

    pip install bobocep

Once this is done, you can begin importing :code:`bobocep` into your own project.
