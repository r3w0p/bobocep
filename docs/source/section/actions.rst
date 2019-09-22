Actions
*******


Create Action
=============

To create your own action, you need to create a class that extends from the :code:`BoboAction` type, as follows.

.. code:: python

    from bobocep.rules.actions.bobo_action import BoboAction
    from bobocep.rules.events.bobo_event import BoboEvent

    class MyAction(BoboAction):

        def _perform_action(self, event: BoboEvent) -> bool:
            // ...

Then, implement the :code:`_perform_action` method and put whatever action you want to execute in there.
Make the method return :code:`True` if your action was successfully executed, and :code:`False` otherwise.

Then, you can execute the action in the future using the :code:`execute` interface, as follows.

.. code:: python

    my_action = MyAction()
    success, exception = my_action.execute(my_event)

This will return the success of the action execution, as well as any exception that was raised if unsuccessful, or
:code:`None` if no exception was raised.


Multi Actions
=============

If you want to execute multiple actions, you can use a subclass of the :code:`MultiAction` type.
For example, if you want to execute a sequence of actions, you can use :code:`SequentialAction`, as follows.

.. code:: python

    from bobocep.rules.actions.multi.sequential_action import SequentialAction

    seq_act = SequentialAction(actions=[act_1, act_2, act_n])
