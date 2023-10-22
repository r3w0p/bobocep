Use Cases
*********

Assisted Living
===============

An area of interest in Internet of Things is the need for Smart Home solutions
that are designed for people with disability and mobility needs in order to
provide independent
`Assisted Living <https://en.wikipedia.org/wiki/Assisted_living>`_.

This could be accomplished through sensors that trigger events with minimal or
unconventional means of interaction by the end user, such as through voice,
controllers, or simply human presence.
Actuators, such as plugs, locks, kitchen appliances, and alarms, can trigger
as a consequence of these minimal human interactions.
Assisted Living can leverage the low-latency event detection and actuation
from :code:`BoboCEP` to ensure a reliable and rapid response to events.


Phenomenon
----------

Consider a single phenomenon that one might wish to detect and automatically
respond to in an Assisted Living solution.
For example, if an elderly resident were to fall in their home or living
facility and require immediate assistance, then this 'phenomenon' could be
detected through one or more different patterns of correlated, temporal data.

.. raw:: html

    <details>
    <summary><a>Code</a></summary>
    </br>

.. code:: python

    phenom_fall = BoboPhenomenon(
        name="Fall",
        patterns=[pattern_1, pattern_2, pattern_3],
        action=action_fall
    )

.. raw:: html

    </details>
    </br>


Pattern #1
^^^^^^^^^^

A person is detected entering a room and they have not been detected moving
for at least :code:`60` seconds, nor detected leaving the room.

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
^^^^^^^^^^

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
^^^^^^^^^^

Rapid change in accelerometer readings on smart wearable device, followed by
no significant movement and calls for help via the nearby microphone.

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
-------

On fulfilment of the phenomenon via any of its patterns, a complex event is
generated and one or more actions may be triggered.

For this, we could use the :code:`BoboActionMultiSequential` action, which
takes multiple actions and runs them sequentially.
It can attempt to run them all in sequence and continue execution even if
some of them were to fail.
This is useful for our scenario because we can trigger several actions for
redundancy.
For example, we can notify multiple neighbours of the emergency even if some
requests failed to send.

.. raw:: html

    <details>
    <summary><a>Code</a></summary>
    </br>

.. code:: python

    action_fall = BoboActionMultiSequential(
        name="Action Fall",
        actions=[action_unlock_door, action_notify_neighbours],
        stop_on_fail=False
    )

.. raw:: html

    </details>
    </br>


Action #1
^^^^^^^^^

Unlock the front door, to allow for easy access by neighbours, care workers,
or paramedics.

Below is a custom action, :code:`BoboActionIFTTTWebhooks`, that uses the
`IFTTT Webhooks Integration <https://ifttt.com/maker_webhooks>`_ to
accomplish this.
A Webhooks request can trigger various smart locks that are integrated
into the IFTTT service.
For example, `Kubu <https://ifttt.com/kubu_smart_lock>`_ or
`Nuki <https://ifttt.com/nuki>`_.

The :code:`webhooks_event_name` parameter is the custom Event Name that is
entered when setting up the Webhooks integration.
The :code:`webhooks_key` is provided in the Webhooks Documentation that
appears `here <https://ifttt.com/maker_webhooks>`_ after making an event.

.. raw:: html

    <details>
    <summary><a>Code</a></summary>
    </br>

.. code:: python

    from typing import Tuple, Any
    from bobocep.cep.action import BoboAction
    from bobocep.cep.event import BoboEventComplex
    import requests


    class BoboActionIFTTTWebhooks(BoboAction):
        """
        An action that triggers an event using the IFTTT Webhooks integration.
        See: https://ifttt.com/maker_webhooks
        """

        _URL = "https://maker.ifttt.com/trigger/{0}/json/with/key/{1}"

        def __init__(
                self,
                name: str,
                webhooks_event_name: str,
                webhooks_key: str,
                *args,
                **kwargs):
            """
            :param name: The action name.
            :param webhooks_event_name: IFTTT Webhooks event name.
            :param webhooks_key: IFTTT Webhooks key.
            :param args: Action arguments.
            :param kwargs: Action keyword arguments.
            """
            super().__init__(name=name, args=args, kwargs=kwargs)

            self._webhooks_event_name = webhooks_event_name
            self._webhooks_key = webhooks_key

        def execute(self, event: BoboEventComplex) -> Tuple[bool, Any]:
            """
            :param event: The complex event that triggered the action.

            :return: A tuple containing:
                     whether the event request was sent successfully; and
                     the name of the event that was sent.
            """
            response = requests.get(self._URL.format(
                self._webhooks_event_name,
                self._webhooks_key))

            return response.ok, self._webhooks_event_name

.. raw:: html

    </details>
    </br>


Action #2
^^^^^^^^^

Notify a neighbour via SMS.

Below is a custom action, :code:`BoboActionTwilioSMS`, that uses the
`Twilio SMS API <https://www.twilio.com/docs/sms>`_ to accomplish this.
Note: the code below requires the additional
`twilio <https://pypi.org/project/twilio/>`_ package.

.. raw:: html

    <details>
    <summary><a>Code</a></summary>
    </br>

.. code:: python

    from typing import Tuple, Any
    from bobocep.cep.action import BoboAction
    from bobocep.cep.event import BoboEventComplex
    from twilio.rest import Client  # https://pypi.org/project/twilio/


    class BoboActionTwilioSMS(BoboAction):
        """
        An action that sends an SMS via the Twilio API.
        """

        def __init__(
                self,
                name: str,
                account_sid: str,
                auth_token: str,
                num_from: str,
                num_to: str,
                message: str,
                *args,
                **kwargs):
            """
            :param name: The action name.
            :param account_sid: Twilio Account SID.
            :param auth_token: Twilio Auth Token.
            :param num_from: Twilio phone number.
            :param num_to: Recipient phone number.
            :param message: Message to send to recipient.
            :param args: Action arguments.
            :param kwargs: Action keyword arguments.
            """
            super().__init__(name=name, args=args, kwargs=kwargs)

            self._client = Client(account_sid, auth_token)
            self._num_from = num_from
            self._num_to = num_to
            self._message = message

        def execute(self, event: BoboEventComplex) -> Tuple[bool, Any]:
            """
            :param event: The complex event that triggered the action.

            :return: A tuple containing:
                     whether the SMS was sent successfully; and
                     the recipient phone number.
            """
            message = self._client.messages.create(
                from_=self._num_from,
                body=self._message,
                to=self._num_to
            )

            success = message.status in ("delivered", "queued", "sending", "sent")
            return success, self._num_to

.. raw:: html

    </details>
    </br>


Or, notify multiple neighbours with a sequential action.

Each action in :code:`actions` below would be an instance of
:code:`BoboActionTwilioSMS` but with differing :code:`num_to` values,
which represents the recipient's phone number.

.. raw:: html

    <details>
    <summary><a>Code</a></summary>
    </br>

.. code:: python

    action_notify_neighbours = BoboActionMultiSequential(
        name="Notify Neighbours",
        actions=[action_neighbour_1, action_neighbour_2],
        stop_on_fail=False
    )

.. raw:: html

    </details>
    </br>
