Glossary
********




Bobo Events
===========

Data types used in :code:`bobocep` to represent different system events.

PrimitiveEvent
--------------

Represents data that has entered the :code:`bobocep` system.

CompositeEvent
--------------

Represents the inference of a complex event.

ActionEvent
-----------

Represents the execution of an action by the system.




Complex Event
=============

An event that represents the inference of some phenomenon that was identified by a pattern in a data stream.




Contiguity
==========

The policy of states with regard to how they react to events that do not cause a state transition.
:code:`bobocep` supports the following three types of contiguity.

Strict
------

All matching events are *strictly* one after the other, without any non-matching events in-between.
If an event does not match, the run halts.

Relaxed
-------

Any non-matching events are ignored.

Non-Deterministic Relaxed
-------------------------

The same as relaxed, but allows multiple matches from a state when its transition is non-deterministic.




History
=======

The events that were accepted by a pattern as being indicative of the existence of a complex event.




Null Data
=========

Arbitrary static data that is periodically inserted into the CEP system.
It has several purposes:

- Provides state clearance, so that runs always have a periodic event with which to trigger time window checks.
- So runs can reach the accepting state if *nothing* happens i.e. check if a null event occurs instead.




Pattern
=======

A sequence of data correlations that, when fulfilled with data from a data stream, infer the existence of a complex
event.




Run
===

An instance of a pattern.




State Clearance
===============

Ensuring that runs are always eventually halted and removed from memory, to prevent a build-up of
incomplete runs with no means of halting.
This is typically achieved by adding a time window to patterns that will cause an eventual halt
if a run is not fulfilled within a given time frame.




States
======

Start State
-----------

The first state of an automaton that triggers the generation of a new run when reached.


Accepting State
---------------

The final state of an automaton that triggers the generation of a complex event when reached.

