Installation
************

The :code:`bobocep` software is `hosted on PyPi <https://pypi.org/project/bobocep/>`_.
You can download the latest version via :code:`pip` using the following command:

.. code:: console

    pip install bobocep


Message Broker
==============

:code:`bobocep` relies on the use of an external message broker to network multiple software instances
together in order to provide the active replication of partially-completed complex events.
You can connect to any message broker that is compatible with the `AMQP 0-9-1 <https://www.amqp.org/>`_ protocol,
such as `RabbitMQ <https://www.rabbitmq.com/>`_.

A message broker is optional, and is only required if you want to distribute :code:`bobocep` across multiple devices.
