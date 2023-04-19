Actions
*******

On the completion of a pattern's run, the Producer is notified and
produces a complex event in response, which represents the detection
of the pattern's phenomenon.

The Producer then notifies the Forwarder that the phenomenon's action
should be executed in response.

.. code:: python

    def execute(self, event: BoboEventComplex) -> Tuple[bool, Any]:
        ...

On action execution, the :code:`execute` function is provided with a
copy of the complex event, and is expected to return two things:

#. Whether the action was successful or not:
   :code:`True` or :code:`False`, accordingly.

#. Any additional data, or :code:`None`. Note that, if using Distributed
   :code:`BoboCEP`, the data type should be JSONable.
   See `Distributed <distributed.html>`_ for more information.


Handlers
========

In :code:`BoboCEP`, Forwarder contains an **action handler** which
is responsible for executing actions and passing the action's response
back.
The Forwarder then generates an action event which is sent to Receiver.

The default action handlers provided by :code:`BoboCEP` are as follows.


Blocking
--------

The blocking handler blocks the thread on which :code:`BoboCEP`
is running on while it executes its actions.
This is useful when :code:`BoboCEP` is required to execute actions
deterministically, *one action at a time*, in the order that they are
sent to Forwarder.

.. code:: python

    from bobocep.cep.action import BoboActionHandlerBlocking

    handler = BoboActionHandlerBlocking()


Multithreading
--------------

The multithreading handler uses :code:`n` threads to execute actions
concurrently.

.. code:: python

    from bobocep.cep.action import BoboActionHandlerMultithreading

    handler = BoboActionHandlerMultithreading(threads=5)


Multiprocessing
---------------

The multiprocessing handler utilises multicore processing by specifying
uses :code:`n` processes on which to execute actions simultaneously.

.. code:: python

    from bobocep.cep.action import BoboActionHandlerMultiprocessing
    from multiprocessing import cpu_count

    # Processes equal to one less than the maximum system CPUs available.
    handler = BoboActionHandlerMultiprocessing(processes=max(1, cpu_count() - 1))
