---
title: 'BoboCEP: a Fault-Tolerant Complex Event Processing Engine for Edge Computing in Internet of Things'

tags:
  - complex event processing
  - edge computing
  - internet of things
  - python

authors:
  - name: Alexander Power
    orcid: 0000-0001-5348-7068
    affiliation: 1

affiliations:
 - name: Department of Computer Science, University of Bath, United Kingdom
   index: 1

date: DD Month YYYY
bibliography: paper.bib
---

# Summary

*Internet of Things* (IoT) systems rely on a multitude of heterogeneous hardware, software, services, and standards to represent Internet-connected *Things* and their environments.
However, despite this heterogeneity, emerging standardisation efforts [@W3C:WoT:TD] have recognised three core affordances applicable to all Things, namely:
(1) *properties*, the internal states of a Thing;
(2) *events*, significant state changes within a Thing; and
(3) *actions*, invocations of state changes onto a Thing.

`BoboCEP` is a *Complex Event Processing* (CEP) engine designed for edge computing in IoT systems that is able to provide a reliable platform on which to implement all three essential Thing affordances.
This makes it a unified, dependable platform on which to base IoT system development that is privacy-focussed by keeping data flow and processing at the network edge.
For example, a developer considers what *phenomena* they would like `BoboCEP` to be able to detect and denotes one or more *patterns* that must emerge in the data stream that, if fulfilled by the relevant data, would infer the existence of a given phenomenon.
On pattern fulfilment, an action may be executed.
The data stream represents properties from various Things, the fulfilment of a pattern represents event detection, and the action affordance is applicable on event detection.

# Statement of Need

`BoboCEP` has existed for several years as a CEP engine to provide inferential reasoning and decision-making on streaming data [@Power:2020] and has been under significant development ever since to become a robust platform on which to deploy IoT systems.
It adopts an *information flow processing* (IFP) architecture that consumes a data stream from diverse sources (i.e., Things) [@Cugola:2012].
These data enter the system in a serialised and uncorrelated manner (i.e., *simple* events), which are then compared against user-designed *patterns* that seek to recognise temporal relationships.
If data satisfies its conditions, then a *complex* event is generated and an action may be executed consequently.

Unlike other CEP systems, which focus on cloud-based big data platforms [@Giatrakos:2020], `BoboCEP` is designed for dependable edge computing in IoT systems by extending the IFP architecture to additionally provide *fault tolerance* (FT) via the active replication of partially completed complex events across multiple instances of the software.
That is, it can be deployed on $n$ devices across the network edge and is able to protect the system against, at most, $n-1$ software failures.
This is crucial to ensure that valuable insights into patterns emerging across the ever-changing cyber-physical environment are not missed, leading to events not being recognised and necessary actions not triggering.

# Use Case

The dependable processing of live data streams at the network edge presents many possibilities for IoT applications.
For example, [@Rocha:2021] recognise the need for Smart Home solutions that are designed for people with disability and mobility needs in order to provide independent *assisted living*.
This is accomplished through sensors that trigger events with minimal or unconventional means of interaction by the end user, such as through voice, eye movement, bespoke GUIs/controllers, or simply human presence.
Actuators, such as plugs, locks, kitchen appliances, and alarms, can trigger because of this minimal human input.

Assisted living can leverage low-latency event detection and actuation provided by `BoboCEP` to ensure a reliable and rapid response to environmental phenomena.
For example, if an elderly resident were to fall in their home and require an ambulance, then this 'phenomenon' could be detected through one-or-more different patterns of correlated, temporal data.
The patterns may be:

1. A person is detected entering a room and they have not been detected moving for at least `30` seconds, nor detected leaving the room, nor any indication through some other modality (e.g., microphone, interaction with home appliances).
2. An attached heart-rate sensor has stopped providing data, or has been consistently reporting dangerously low readings.
3. Calls for help are heard via the microphone or a virtual assistant system.

On fulfilment of the phenomenon via any pattern, a complex event is generated and an action may be triggered to:

- Call for an ambulance.
- Notify neighbours.
- Unlock the front door.

Furthermore, [@Scattone:2021] cite `BoboCEP` as a relevant technology even in the context of large-scale solutions, such as Smart Cities, where `BoboCEP` may only send events of high importance to the cloud.
Indeed, the assisted living scenario is directly applicable: most data can stay privately within the home network (e.g., heart-rate data, location of people in their homes), but calling for an ambulance and notifying neighbours can leverage cloud services.

Due to the critical nature of assisted living, `BoboCEP` may run in a distributed manner over multiple devices/software instances.
This mode uses active replication to maintain consistent state over each instance so that, if one instance fails, then detecting and reporting phenomena would not be impeded.
This design provides the additional benefit of being able to load-balance data input across all instances, which helps the solution to scale to a vast number of sensors and actuators.

# Acknowledgements

I acknowledge contributions from Dr Gerald Kotonya for assisting in the design of `BoboCEP` in its earlier versions, helping to shape the project into what it has become.

# References
