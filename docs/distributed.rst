Distributed
***********

:code:`BoboCEP` is able to be distributed over multiple instances for
fault-tolerant CEP at the network edge.

.. note:: Distributed :code:`BoboCEP` is designed to be deployed at the edge
          of a single network, ideally with 2-3 instances of the software.


Recovery Scenarios
==================

:code:`BoboCEP` is designed to handle errors and discrepancies with distributed
processing in the least complex way possible, that does not rely on excessive
message passing as part of its recovery strategy. Various scenarios, and their
expected recovery strategies, are discussed below.


Scenario #: cannot communicate with another instance.
-----------------------------------------------------

TODO


Scenario #: multiple instances complete same run with different events.
------------------------------------------------------------------------

TODO


Scenario #: one instance completes run, another halts it.
----------------------------------------------------------

TODO


Scenario #: one instance updates run, another halts it.
----------------------------------------------------------

TODO


Scenario #: run update is multiple steps ahead of local run.
-------------------------------------------------------------

TODO
