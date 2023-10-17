Use Case
********

An area of interest in Internet of Things is the need for Smart Home solutions that are designed for people with disability and mobility needs in order to provide independent `Assisted Living <https://en.wikipedia.org/wiki/Assisted_living>`_.

This could be accomplished through sensors that trigger events with minimal or unconventional means of interaction by the end user, such as through voice, controllers, or simply human presence.
Actuators, such as plugs, locks, kitchen appliances, and alarms, can trigger as a consequence of these minimal human interactions.
Assisted Living can leverage the low-latency event detection and actuation from :code:`BoboCEP` to ensure a reliable and rapid response to events.


Phenomenon
==========

Consider a single phenomenon that one might wish to detect and automatically respond to in an Assisted Living solution.
For example, if an elderly resident were to fall in their home or living facility and require immediate assistance, then this 'phenomenon' could be detected through one or more different patterns of correlated, temporal data.


Pattern #1
----------

A person is detected entering a room and they have not been detected moving for at least :code:`60` seconds, nor detected leaving the room.

.. raw:: html

    <details>
    <summary><a>Code</a></summary>
    </br>


.. code:: python

    TODO


.. raw:: html

    </details>
    </br>


Pattern #2
----------

A heart-rate sensor has been consistently reporting dangerously low readings.

.. raw:: html

    <details>
    <summary><a>Code</a></summary>
    </br>


.. code:: python

    TODO


.. raw:: html

    </details>
    </br>


Pattern #3
----------

Rapid change in accelerometer readings on smart wearable device, followed by no significant movement and calls for help via the nearby microphone.

.. raw:: html

    <details>
    <summary><a>Code</a></summary>
    </br>


.. code:: python

    TODO


.. raw:: html

    </details>
    </br>


Actions
=======

On fulfilment of the phenomenon via any of its patterns, a complex event is generated and one or more actions may be triggered.

For this, we could use the :code:`BoboActionMultiSequential` action, which takes multiple actions and runs them sequentially.
It can attempt to run them all in sequence and continue execution even if some of them were to fail.
This is useful for our scenario because we can trigger several actions for redundancy.
For example, we can notify multiple neighbours of the emergency even if some requests failed to send.

.. raw:: html

    <details>
    <summary><a>Code</a></summary>
    </br>


.. code:: python

    TODO


.. raw:: html

    </details>
    </br>


Action #1
---------

.. raw:: html

    <details>
    <summary><a>Code</a></summary>
    </br>


.. code:: python

    TODO


.. raw:: html

    </details>
    </br>


Action #2
---------

.. raw:: html

    <details>
    <summary><a>Code</a></summary>
    </br>


.. code:: python

    TODO


.. raw:: html

    </details>
    </br>


Deployment
==========

Putting this all together, we can deploy :code:`BoboCEP` as follows.

.. raw:: html

    <details>
    <summary><a>Code</a></summary>
    </br>


.. code:: python

    phenom = BoboPhenomenon(
        name="fall",
        patterns=[pattern_1, pattern_2, pattern_3],
        action=BoboActionMultiSequential(TODO)
    )


.. raw:: html

    </details>
    </br>

