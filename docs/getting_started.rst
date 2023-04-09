Getting Started
***************


Complex Event Processing
========================

The primary goal of :code:`BoboCEP` is to take streaming data that enters a
system in a serialised and uncorrelated manner (i.e. **simple events**),
and detect temporal **patterns** using it to infer the occurrence of some
higher-level **phenomenon**.
This, in turn generates a **complex event** representing the detection of the
phenomenon, and **action events** representing the actions taken in response.
These events are added to the data stream, where they can be used for future
pattern detection.

For example, an office may wish to detect the phenomenon of an office fire
through various data patterns that could infer its occurrence.
Patterns may include:

#. A sharp rise in temperature sensor readings, followed by smoke detection
   within 1 minute of the rise in temperature.
#. Significant movement away from working spaces and towards the fire exit.
#. Or, it may simply be the pressing of the fire alarm, with no further
   correlations necessary.

When any of these patterns are fulfilled by the expected data, a number of
actions may be triggered as a response: fire alarms sound, sprinklers are
activated, and so on.


BoboCEP Architecture
====================

The architecture of :code:`BoboCEP` is based on the
*information flow processing* (IFP) architecture proposed by [CM2012]_.
This architecture is extended by enabling state updates to be synchronised
across multiple instances of :code:`BoboCEP` across a network for fault
tolerance.

TODO architecture diagram

The four subsystems of :code:`BoboCEP`:

- **Receiver**.
  The entry point for data into the system. Its purpose is to validate
  incoming data and then format it into a **simple event**.
  It also consumes **complex events** and **action events** and introduces
  these event types into the data stream.

- **Decider**.
  Manages **runs**, which represent **patterns** that have not yet received all
  of the data necessary to indicate the occurrence of some phenomenon.
  See `Phenomena <phenomena.html>`_ for more information.

- **Producer**.
  Generates **complex events** when it receives notification from Decider
  that a run has completed and, therefore, a phenomenon has been observed
  which the complex event represents.

- **Forwarder**.
  Forwards actions passed to it by Producer and executes them. This may involve
  communication with external services. Each action leads to the generation of
  an **action event** that details what occurred during action execution.
  See `Actions <actions.html>`_ for more information.

This architecture is extended by enabling state updates to be synchronised
across multiple instances of :code:`BoboCEP`.
See `Distributed <distributed.html>`_ for more information.


Quick Setup
===========

For a quick setup, we will create a :code:`BoboSetup` instance.

TODO


Next Steps
==========

TODO


Why "Bobo"?
===========

Bobo is the name of Mr Burns' childhood teddy bear that features in the episode
"`Rosebud  <https://en.wikipedia.org/wiki/Rosebud_(The_Simpsons)>`_"
of The Simpsons.


References
==========

.. [CM2012]
    Cugola, G., & Margara, A. (2012).
    `Processing flows of information: From data stream to complex event processing
    <https://doi.org/10.1145/2187671.2187677>`_.
    *ACM Computing Surveys (CSUR)*, *44*\(3), 15.
