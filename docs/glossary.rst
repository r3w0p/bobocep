Glossary
********


Contiguity
==========

The policy for how :code:`BoboCEP` should respond when it is unable to match an event to a :ref:`glossary:Run`.


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




Events
======


Simple Event
------------

Represents primitive data that has entered the :code:`BoboCEP` system via the Receiver from an external source.


Complex Event
-------------

Represents the inference of some phenomenon that was identified by a pattern in other events.


Action Event
------------

Represents the execution of an action by the system and the effect of its execution, if any.


Event History
-------------

The events that were accepted by a pattern as being indicative of the existence of a complex event.




Process
=======


Pattern
-------

A sequence of data correlations that, when fulfilled with data from a data stream, infer the existence of a complex
event.


Run
---

An instance of a pattern.
