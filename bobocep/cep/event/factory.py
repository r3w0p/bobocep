# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

"""
Event factory.
"""

from json import loads

from bobocep.cep.event.event import BoboEventError, BoboEvent


class BoboEventFactoryError(BoboEventError):
    """
    An event factory error.
    """


class BoboEventFactory:
    """
    A BoboEvent factory that generates instances from JSON representations
    of events.
    """

    @staticmethod
    def from_json_str(j: str) -> BoboEvent:
        """
        :param j: A JSON `str` representation of the event.
        :return: A new instance of the event type.

        :raises BoboEventFactoryError: If `EVENT_TYPE` key is missing
            from JSON.
        :raises BoboEventFactoryError: If `EVENT_TYPE` value is an unknown
            event type.
        """
        from bobocep.cep.event.action import BoboEventAction
        from bobocep.cep.event.complex import BoboEventComplex
        from bobocep.cep.event.simple import BoboEventSimple

        d: dict = loads(j)

        if BoboEvent.EVENT_TYPE not in d:
            raise BoboEventFactoryError(
                "Missing key '{}'.".format(BoboEvent.EVENT_TYPE))

        if d[BoboEvent.EVENT_TYPE] == BoboEventSimple.TYPE_SIMPLE:
            return BoboEventSimple.from_json_dict(d)

        if d[BoboEvent.EVENT_TYPE] == BoboEventComplex.TYPE_COMPLEX:
            return BoboEventComplex.from_json_dict(d)

        if d[BoboEvent.EVENT_TYPE] == BoboEventAction.TYPE_ACTION:
            return BoboEventAction.from_json_dict(d)

        raise BoboEventFactoryError(
            "Unknown event type '{}'.".format(d[BoboEvent.EVENT_TYPE]))
