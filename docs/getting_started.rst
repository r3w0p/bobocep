Getting Started
***************


Complex Event Processing
========================

The primary goal of :code:`BoboCEP` is to be able to infer the occurrence of
*complex events* via patterns in data.
A simple example might be: a sharp rise in temperature sensor readings,
followed by smoke detection, within 1 minute
of each other, could infer the occurrence of a **fire** in a physical
environment.
When this happens, we notify an external system to start the fire alarms
in the building.

TODO


BoboCEP Architecture
====================

TODO


This architecture is extended by enabling state updates to be synchronised
across multiple instances of :code:`BoboCEP`.
[Elaborate]
See Distributed for more information.


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
That's pretty much it.
