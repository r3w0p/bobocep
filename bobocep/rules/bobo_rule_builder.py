from abc import ABC

from bobocep.rules.events.action_event import ActionEvent
from bobocep.rules.events.bobo_event import BoboEvent
from bobocep.rules.events.composite_event import CompositeEvent
from bobocep.rules.events.histories.bobo_history import BoboHistory
from bobocep.rules.events.primitive_event import PrimitiveEvent
from bobocep.rules.nfas.bobo_nfa import BoboNFA
from bobocep.rules.nfas.patterns.bobo_pattern import BoboPattern
from bobocep.rules.states.bobo_state import BoboState
from bobocep.rules.transitions.bobo_transition import BoboTransition


class BoboRuleBuilder(ABC):
    """Builds rule types from serialized representations of those types."""

    @staticmethod
    def event(d: dict) -> BoboEvent:
        """ Creates either a PrimitiveEvent, CompositeEvent, or ActionEvent
        instance from a serialized representation of one of them.

        :param d: A dict representation of either a PrimitiveEvent,
                  CompositeEvent, or ActionEvent instance.
        :type d: dict

        :return: Either a PrimitiveEvent, CompositeEvent, or ActionEvent
                 instance, returned by their common superclass BoboEvent.
        """

        if ActionEvent.FOR_EVENT in d:
            return BoboRuleBuilder.action(d)
        elif CompositeEvent.NAME in d:
            return BoboRuleBuilder.composite(d)
        else:
            return BoboRuleBuilder.primitive(d)

    @staticmethod
    def primitive(d: dict) -> PrimitiveEvent:
        """Creates a PrimitiveEvent instance from serialized representation of
           one.

        :param d: A dict representation of a PrimitiveEvent instance.
        :type d: dict

        :raises RuntimeError: Timestamp not found in dict.
        :raises RuntimeError: Data not found in dict.

        :return: A PrimitiveEvent instance.
        """

        timestamp = d.get(PrimitiveEvent.TIMESTAMP)
        if timestamp is None:
            raise RuntimeError("Timestamp not found in dict.")

        data = d.get(PrimitiveEvent.DATA)
        if data is None:
            raise RuntimeError("Data not found in dict.")

        event_id = d.get(PrimitiveEvent.EVENT_ID)
        if event_id is None:
            raise RuntimeError("Event ID not found in dict.")

        return PrimitiveEvent(timestamp=timestamp,
                              data=data,
                              event_id=event_id)

    @staticmethod
    def composite(d: dict) -> CompositeEvent:
        """Creates a CompositeEvent instance from a serialized representation
        of one.

        :param d: A dict representation of a CompositeEvent instance.
        :type d: dict

        :raises RuntimeError: Timestamp not found in dict.
        :raises RuntimeError: Name not found in dict.
        :raises RuntimeError: History not found in dict.
        :raises RuntimeError: Event ID not found in dict.

        :return: A CompositeEvent instance.
        """

        timestamp = d.get(CompositeEvent.TIMESTAMP)
        if timestamp is None:
            raise RuntimeError("Timestamp not found in dict.")

        name = d.get(CompositeEvent.NAME)
        if name is None:
            raise RuntimeError("Name not found in dict.")

        history_dict = d.get(CompositeEvent.HISTORY)
        if history_dict is None:
            raise RuntimeError("History not found in dict.")

        history = BoboRuleBuilder.history(history_dict)
        data = d.get(BoboEvent.DATA)

        event_id = d.get(CompositeEvent.EVENT_ID)
        if event_id is None:
            raise RuntimeError("Event ID not found in dict.")

        return CompositeEvent(timestamp=timestamp,
                              name=name,
                              history=history,
                              data=data,
                              event_id=event_id)

    @staticmethod
    def action(d: dict) -> ActionEvent:
        """Creates an ActionEvent instance from a serialized representation of
           one.

        :param d: A dict representation of an ActionEvent instance.
        :type d: dict

        :raises RuntimeError: Timestamp not found in dict.
        :raises RuntimeError: Name not found in dict.
        :raises RuntimeError: Success not found in dict.
        :raises RuntimeError: For Event dict not found in dict.
        :raises RuntimeError: Event ID not found in dict.

        :return: An ActionEvent instance.
        """

        timestamp = d.get(ActionEvent.TIMESTAMP)
        if timestamp is None:
            raise RuntimeError("Timestamp not found in dict.")

        name = d.get(ActionEvent.NAME)
        if name is None:
            raise RuntimeError("Name not found in dict.")

        success = d.get(ActionEvent.SUCCESS)
        if success is None:
            raise RuntimeError("Success not found in dict.")

        for_event_dict = d.get(ActionEvent.FOR_EVENT)
        if for_event_dict is None:
            raise RuntimeError("For Event dict not found in dict.")

        for_event = BoboRuleBuilder.composite(for_event_dict)
        exception = d.get(ActionEvent.EXCEPTION)
        description = d.get(ActionEvent.DESCRIPTION)
        data = d.get(ActionEvent.DATA)

        event_id = d.get(BoboEvent.EVENT_ID)
        if event_id is None:
            raise RuntimeError("Event ID not found in dict.")

        return ActionEvent(timestamp=timestamp,
                           name=name,
                           success=success,
                           for_event=for_event,
                           exception=exception,
                           description=description,
                           data=data,
                           event_id=event_id)

    @staticmethod
    def history(d: dict) -> BoboHistory:
        """Creates a BoboHistory instance from serialized representation of
           one.

        :param d: A dict representation of a BoboHistory instance.
        :type d: dict

        :return: A BoboHistory instance.
        """

        event_history_dict = {}

        for key in d.keys():
            key_events = d[key]

            event_history_dict[key] = []

            for event_dict in key_events:
                event_history_dict[key].append(
                    BoboRuleBuilder.event(event_dict))

        return BoboHistory(events=event_history_dict)

    @staticmethod
    def nfa(name_nfa: str, pattern: BoboPattern) -> BoboNFA:
        """Generates a named NFA from a pattern.

        :param name_nfa: The name for the automaton instance.
        :type name_nfa: str

        :param pattern: The pattern to use for the automaton definition.
        :type pattern: BoboPattern

        :raises RuntimeError: Pattern does not contain any layers.
        :raises RuntimeError: The start and the final state must not
                              contain loops, be negated, be optional, or be
                              nondeterministic.
        :raises RuntimeError: State names must be unique.

        :return: A new BoboNFA instance.
        """

        if len(pattern.layers) == 0:
            raise RuntimeError("Pattern does not contain any layers.")

        nfa_states = {}
        nfa_transitions = {}
        nfa_start_state_name = None
        nfa_final_state_name = None
        nfa_preconditions = pattern.preconditions
        nfa_haltconditions = pattern.haltconditions

        all_state_names = []
        last_state_names = None
        last_states = None
        last_layer = None
        len_layers = len(pattern.layers)

        for i, layer in enumerate(pattern.layers):

            # start / final states must be "normal"
            if (i == 0 or i == len_layers - 1) and (layer.loop or layer.negated
                                                    or layer.optional or
                                                    len(layer.predicates) > 1):
                raise RuntimeError("The start and final states must "
                                   "not contain loops, be negated, be "
                                   "optional, or be nondeterministic")

            for j in range(layer.times):
                state_names = []
                states = []

                for k, predicate in enumerate(layer.predicates):
                    state_name = "{}-{}-{}".format(layer.label, k + 1, j + 1)

                    state_names.append(state_name)
                    states.append(BoboState(state_name,
                                            layer.label,
                                            predicate,
                                            negated=layer.negated,
                                            optional=layer.optional))

                # first state is the start state
                if i == 0 and j == 0:
                    nfa_start_state_name = state_names[0]

                # last state is the final state
                if i == len_layers - 1 and j == layer.times - 1:
                    nfa_final_state_name = state_names[-1]

                # duplicate state name found
                for state_name in state_names:
                    if state_name in all_state_names:
                        raise RuntimeError("State names must be unique. "
                                           "Multiple uses found for name {}."
                                           .format(state_name))

                # add state name to list of current state names
                all_state_names.extend(state_names)

                # add states
                for state in states:
                    nfa_states[state.name] = state

                # add transitions for previous state(s)
                if last_state_names is not None and last_states is not None \
                        and last_layer is not None:

                    # include last layer's state (would only be one) if looping
                    if last_layer.loop:
                        state_names.extend(last_state_names)

                    # create transition and apply it to the previous state(s)
                    transition = BoboTransition(state_names=state_names,
                                                strict=layer.strict)
                    for state in last_states:
                        nfa_transitions[state.name] = transition

                last_state_names = state_names
                last_states = states
                last_layer = layer

        # add empty transition for final state
        nfa_transitions[nfa_final_state_name] = BoboTransition(
            state_names=[], strict=False)

        return BoboNFA(name=name_nfa,
                       states=nfa_states,
                       transitions=nfa_transitions,
                       start_state_name=nfa_start_state_name,
                       final_state_name=nfa_final_state_name,
                       preconditions=nfa_preconditions,
                       haltconditions=nfa_haltconditions)
