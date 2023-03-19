# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

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
        from bobocep.cep.event.action import BoboEventAction
        from bobocep.cep.event.complex import BoboEventComplex
        from bobocep.cep.event.simple import BoboEventSimple

        """
        :param j: A JSON string representation of an object of this type.
        :return: A new BoboEvent instance of its type.

        :raises BoboEventFactoryError: If `EVENT_TYPE` key is missing
            from JSON.
        :raises BoboEventFactoryError: If `EVENT_TYPE` value is an unknown
            event type.
        """
        d: dict = loads(j)

        if BoboEvent.EVENT_TYPE not in d:
            raise BoboEventFactoryError(
                "Missing key '{}'.".format(BoboEvent.EVENT_TYPE))

        if d[BoboEvent.EVENT_TYPE] == BoboEventAction.TYPE_ACTION:
            return BoboEventAction.from_dict(d)

        if d[BoboEvent.EVENT_TYPE] == BoboEventComplex.TYPE_COMPLEX:
            return BoboEventComplex.from_dict(d)

        if d[BoboEvent.EVENT_TYPE] == BoboEventSimple.TYPE_SIMPLE:
            return BoboEventSimple.from_dict(d)

        raise BoboEventFactoryError(
            "Unknown event type '{}'.".format(d[BoboEvent.EVENT_TYPE]))
