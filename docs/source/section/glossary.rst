Glossary
********


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

Also relaxed, but allows multiple matches from a state when its transition is non-deterministic.


Complex Event
=============

Finish me.


Event
=====

Finish me.


History
=======

Finish me.


Primitive
---------

Finish me.

Composite
---------

Finish me.


Null Data
=========

Arbitrary static data that is periodically inserted into the CEP system.
It has several purposes:

- Provides state clearance, so that windowed automata have an event to trigger window checks.
- As a workaround to design automata that can reach the accepting state if *nothing* happens within some time interval
  (i.e. check if a null event is received after the time interval).


Recents
=======

Finish me.


Run
===

Finish me.


State
=====

Finish me.

Accepting State
---------------

The final state of an automaton that triggers the generation of some complex event.


State Clearance
===============

Finish me.


