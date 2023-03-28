from bobocep.cep.action.action import BoboAction
from bobocep.cep.event import BoboEventComplex, BoboEventAction
from bobocep.cep.gen.event_id import BoboGenEventIDUnique
from bobocep.cep.gen.timestamp import BoboGenTimestampEpoch


class BoboActionTrue(BoboAction):
    """An action that is always successful."""

    def __init__(self, name: str = "action"):
        super().__init__(name)

    def execute(self, event: BoboEventComplex) -> BoboEventAction:
        return BoboEventAction(
            event_id=BoboGenEventIDUnique().generate(),
            timestamp=BoboGenTimestampEpoch().generate(),
            data=True,
            phenomenon_name=event.phenomenon_name,
            pattern_name=event.pattern_name,
            action_name=self.name,
            success=True)


class BoboActionFalse(BoboAction):
    """An action that is always unsuccessful."""

    def __init__(self, name: str = "action"):
        super().__init__(name)

    def execute(self, event: BoboEventComplex) -> BoboEventAction:
        return BoboEventAction(
            event_id=BoboGenEventIDUnique().generate(),
            timestamp=BoboGenTimestampEpoch().generate(),
            data=False,
            phenomenon_name=event.phenomenon_name,
            pattern_name=event.pattern_name,
            action_name=self.name,
            success=False)
