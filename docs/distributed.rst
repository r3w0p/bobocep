Distributed
***********

:code:`BoboCEP` is able to be distributed over multiple instances for
fault-tolerant CEP at the network edge.

.. note:: Distributed :code:`BoboCEP` is designed to be deployed at the edge
          of a single network, ideally with only 2-3 software instances.


:code:`UPDATE`

:code:`HALT`

:code:`COMPLETE`

:code:`PING`

:code:`SYNC`


Recovery Scenarios
==================

:code:`BoboCEP` is designed to handle errors and discrepancies with distributed
processing in the least complex way possible, that does not rely on excessive
message passing as part of its recovery strategy. Various scenarios, and their
expected recovery strategies, are discussed below.

The scenarios below consider three distributed instances -
:code:`A`, :code:`B`, and :code:`C` -
that are hosted on three separate devices.


Communication Failure
---------------------

Cannot communicate with another instance.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

TODO


Run Complete
------------

Multiple instances complete same run with different events.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

TODO


Run Halt
--------

One instance completes run, another halts it.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:code:`A` receives
:code:`COMPLETE` from :code:`B`, but receives
:code:`HALT` from :code:`C`
for the same run.

In this scenario, :code:`COMPLETE` takes precedent over :code:`HALT`, and
:code:`A` will complete the run, producing a complex event accordingly.
It will do this if the run is in progress, or if it has been halted locally.
It will not produce a complex event if the run was already completed locally.


Run Update
----------

Update is multiple blocks ahead of local run.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:code:`A` receives an update for a run, where the update is several
blocks ahead of where its local copy of the run is.

In this scenario, the local run is simply pushed forward to the new block, and
the event history of the update replaces the local run history.


Update is behind local run.
^^^^^^^^^^^^^^^^^^^^^^^^^^^

In this scenario, the update is ignored.


One instance updates run, another halts it.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

TODO
