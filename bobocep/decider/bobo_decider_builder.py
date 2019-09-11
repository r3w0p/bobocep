from abc import ABC

from bobocep.decider.buffers.match_event import MatchEvent
from bobocep.decider.buffers.shared_versioned_match_buffer import \
    SharedVersionedMatchBuffer
from bobocep.decider.runs.bobo_run import BoboRun
from bobocep.decider.versions.run_version import RunVersion
from bobocep.rules.bobo_rule_builder import BoboRuleBuilder
from bobocep.rules.nfas.bobo_nfa import BoboNFA


class BoboDeciderBuilder(ABC):
    """A builder for classes related to the :code:`bobocep` decision making
    subsystems.
    """

    @staticmethod
    def match_event(d: dict) -> 'MatchEvent':
        """
        :param d: A dict representation of a MatchEvent instance.
        :type d: dict

        :return: A new MatchEvent instance.
        """

        return MatchEvent(nfa_name=d[MatchEvent.NFA_NAME],
                          label=d[MatchEvent.LABEL],
                          event=BoboRuleBuilder.event(d[MatchEvent.EVENT]),
                          next_ids=d[MatchEvent.NEXT_IDS],
                          previous_ids=d[MatchEvent.PREVIOUS_IDS])

    @staticmethod
    def shared_versioned_match_buffer(d: dict) -> SharedVersionedMatchBuffer:
        """
        :param d: A dict representation of a SharedVersionedMatchBuffer
                  instance.
        :type d: dict

        :return: A new SharedVersionedMatchBuffer instance.
        """

        buffer = SharedVersionedMatchBuffer()

        for eve_dict in d[SharedVersionedMatchBuffer.EVENTS]:
            nfa_name = eve_dict[SharedVersionedMatchBuffer.NFA_NAME]
            match_event = BoboDeciderBuilder.match_event(
                eve_dict[SharedVersionedMatchBuffer.MATCH_EVENT])

            nfa_labels = SharedVersionedMatchBuffer._get_or_create_subdict(
                buffer._eve, nfa_name)
            nfa_events = SharedVersionedMatchBuffer._get_or_create_subdict(
                nfa_labels, match_event.label)
            nfa_events[match_event.event.event_id] = match_event

        for ver_dict in d[SharedVersionedMatchBuffer.LAST]:
            nfa_name = ver_dict[SharedVersionedMatchBuffer.NFA_NAME]
            label = ver_dict[SharedVersionedMatchBuffer.LABEL]
            run_id = ver_dict[SharedVersionedMatchBuffer.RUN_ID]
            version = ver_dict[SharedVersionedMatchBuffer.VERSION]
            event_id = ver_dict[SharedVersionedMatchBuffer.EVENT_ID]

            match_event = buffer._eve[nfa_name][label][event_id]

            nfa_runs = SharedVersionedMatchBuffer._get_or_create_subdict(
                buffer._ver, nfa_name)
            run_versions = SharedVersionedMatchBuffer._get_or_create_subdict(
                nfa_runs, run_id)
            run_versions[version] = match_event

        return buffer

    @staticmethod
    def run(d: dict,
            buffer: SharedVersionedMatchBuffer,
            nfa: BoboNFA) -> 'BoboRun':
        """
        :param d: A dict representation of a BoboRun instance.
        :type d: dict

        :param buffer: A buffer to use with the new BoboRun instance.
        :type buffer: SharedVersionedMatchBuffer

        :param nfa: An automaton to use with the new BoboRun instance.
        :type nfa: BoboNFA

        :return: A new BoboRun instance.
        """

        event = BoboRuleBuilder.event(d[BoboRun.EVENT])
        start_time = d[BoboRun.START_TIME]
        start_state = nfa.states[d[BoboRun.START_STATE_NAME]]
        current_state = nfa.states[d[BoboRun.CURRENT_STATE_NAME]]
        run_id = d[BoboRun.RUN_ID]
        version = RunVersion.list_to_version(d[BoboRun.VERSION])
        last_proceed_had_clone = d[BoboRun.LAST_PROCESS_CLONED]
        halted = d[BoboRun.HALTED]

        return BoboRun(buffer=buffer,
                       nfa=nfa,
                       event=event,
                       start_time=start_time,
                       start_state=start_state,
                       current_state=current_state,
                       run_id=run_id,
                       version=version,
                       put_event=False,
                       last_process_cloned=last_proceed_had_clone,
                       halted=halted)
