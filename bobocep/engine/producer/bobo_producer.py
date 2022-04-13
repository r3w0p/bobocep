from bobocep.engine.bobo_engine_task_publisher import BoboEngineTaskPublisher

from bobocep.engine.bobo_engine_task import BoboEngineTask


class BoboProducer(BoboEngineTask, BoboEngineTaskPublisher):

    def __init__(self):
        super().__init__()

    def update(self) -> None:
        pass  # todo
