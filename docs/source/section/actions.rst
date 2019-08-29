Actions
*******


Create Action
=============

To create your own action, you need to create a class that extends from the :code:`BoboAction` type, as follows.

.. code:: python

    from bobocep.rules.actions.bobo_action import BoboAction
    from bobocep.rules.events.composite_event import CompositeEvent

    class MyAction(BoboAction):

        def perform_action(self, event: CompositeEvent) -> bool:
            // ...

Then, implement the :code:`perform_action` method and put whatever action you want to execute in there.
Make the method return :code:`True` if your action is successful, and :code:`False` if unsuccessful.


Multi Actions
=============

If you want to execute multiple actions, you can use a subclass of the :code:`MultiAction` type.
For example, if you want to execute a sequence of actions, you can use :code:`SequentialAction`, as follows.

.. code:: python

    from bobocep.rules.actions.multi.sequential_action import SequentialAction

    seq_act = SequentialAction(actions=[act_1, act_2, act_n])
