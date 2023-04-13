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

Handler types include:

- **Blocking** handler, which blocks the thread which :code:`BoboCEP`
  is running on while it executes actions.
  This is useful when :code:`BoboCEP` is required to execute actions
  deterministically, one action at a time, in the order that they are
  sent to Forwarder.

- **Pool** handler, which utilises multicore processing for action execution.
  This is useful for most applications which require a higher action
  throughput.
