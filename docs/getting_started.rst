Getting Started
***************


Complex Event Processing
========================

The primary goal of :code:`BoboCEP` is to take streaming data that enters a
system in a serialised and uncorrelated manner (i.e. **simple events**),
and detect temporal **patterns** using it to infer the occurrence of some
higher-level **phenomenon**.
A **complex event** may be generated if a pattern of a phenomenon is fulfilled
with relevant data.
See `Phenomena <phenomena.html>`_ for more information.

On pattern fulfilment, an **action** may be taken in response which, in turn,
leads to the generation of an **action event** representing what happened
during action execution and whether it was successfully executed.
See `Actions <actions.html>`_ for more information.

Complex events and action events are added back into the system's data stream,
where they can be used for further pattern detection.

Example
-------

An office may wish to detect the phenomenon of an office fire
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

.. figure:: ./_static/img/architecture.png
   :alt: Architecture

   :code:`BoboCEP` architecture and external systems.
   Subsystems within dashed border are the core subsystems for a given
   :code:`BoboCEP` instance. Dashed arrows represent data exchange to and from
   external systems (blue, grey).

Subsystems
----------

The :code:`BoboCEP` subsystems are as follows:

- **Receiver**.
  The entry point for data into the system. Its purpose is to validate
  incoming data and then format it into a **simple event**.
  It also consumes **complex events** and **action events** and introduces
  these event types into the data stream.

- **Decider**.
  Manages **runs**, which represent **patterns** that have not yet received all
  of the data necessary to indicate the occurrence of some phenomenon.

- **Producer**.
  Generates **complex events** when it receives notification from Decider
  that a run has completed and, therefore, a phenomenon has been observed
  which the complex event represents.

- **Forwarder**.
  Forwards actions passed to it by Producer and executes them. This may involve
  communication with external services. Each action leads to the generation of
  an **action event** that details what occurred during action execution.

- **Distributed**.
  This architecture is extended by enabling state updates to be synchronised
  across multiple instances of :code:`BoboCEP`.
  See `Distributed <distributed.html>`_ for more information.


Quick Start
===========

The key components to getting started with :code:`BoboCEP` are as follows.

#. Define the `Phenomena <phenomena.html>`_ that you would like to model by
   defining one or more patterns per phenomenon. Use :code:`BoboPatternBuilder`
   for defining patterns to make things much easier.

#. Define `Actions <actions.html>`_ that should be executed if a phenomenon
   were to be triggered. Allocate an action to a phenomenon if you wish, or
   leave it blank.

#. Decide whether you want BoboCEP to be `Distributed <distributed.html>`_ or
   not, and use one of the setup classes to help with setting up the system
   engine and all of its components: :code:`BoboSetupSimple` and
   :code:`BoboSetupSimpleDistributed` are provided for these purposes.

Check out the `Examples <examples.html>`_ page for various ways to
set up :code:`BoboCEP` and connect it to external systems e.g. Flask.


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
