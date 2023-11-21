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
For example, a developer considers what *phenomenon* they would like to detect.
They denote one or more *patterns* that must emerge in the data stream that, if fulfilled by relevant data, infer the existence of the phenomenon.
On pattern fulfilment, an action may be executed.
The data stream represents properties from various Things, the fulfilment of a pattern represents event detection, and the action affordance is applicable on event detection.

# Statement of Need

`BoboCEP` has existed for several years as a CEP engine to provide inferential reasoning and decision-making on streaming data [@Power:2020] and has been under significant development ever since to become a robust platform on which to deploy IoT systems.
It adopts an *information flow processing* (IFP) architecture that consumes a data stream from diverse sources (i.e., Things) [@Cugola:2012].
These data enter the system in a serialised and uncorrelated manner (i.e., *simple* events), which are then compared against user-designed *patterns* that seek to recognise temporal relationships.
If data satisfies its conditions, then a *complex* event is generated and an action may be executed consequently.

`BoboCEP` is designed for dependable edge computing in IoT systems by extending the IFP architecture to additionally provide *fault tolerance* (FT) via the active replication of partially completed complex events across multiple instances of the software.
That is, it can be deployed on $n$ devices across the network edge and is able to protect the system against, at most, $n-1$ software failures.
This is crucial to ensure that valuable insights emerging from the ever-changing cyber-physical environment are not missed, which could lead to events not being detected and actions not executing.

Edge computing is considered an innovative strategy that brings data processing and storage nearer to the end users, not only to alleviate the data processing burden on cloud systems, but also to ensure that private data does not leave the local network [@Alwarafy:2020].
For applications such as smart homes, smart vehicles, and health monitoring, deploying the most appropriate solutions to the edge reduces the probability of data leakage.
For example, data leaks from home cameras and microphones have the ability to cause great distress to end users and lead to the poor adoption of IoT solutions.
Whereas, at the edge, sensitive data can be anonymously processed on-site, with controlled cloud use for further analysis [@Fazeldehkordi:2022].

Many existing CEP systems focus on cloud-based big data platforms [@Giatrakos:2020], or provide 'distributed' computing in a different sense.
`CEPchain` is a solution for integrating CEP and blockchain, but is neither designed for IoT nor edge computing [@Boubeta:2021].
`SAT-CEP-monitor` considers CEP in the context of satellite remote sensing and air quality monitoring only [@Semlali:2021], whereas `BoboCEP` is a generic CEP tool for all edge-based IoT applications.
`CaFtR` focuses on CEP for *fuzzy logic* and uses active replication like `BoboCEP` does [@Xiao:2022], whereas `BoboCEP` is designed around *predicate logic* for deterministic processing behaviour and has used active replication years before their solution.
`EdgeCEP` is the closest system to `BoboCEP` in terms of design and functionality [@Choochotkaew:2017].
However, `BoboCEP` provides resilient event processing in a distributed CEP environment via active replication, whereas `EdgeCEP` is distributed in the sense that it is deployed across a self-organised ad-hoc wireless sensor and actuator network, which does not provide full redundancy to node failure.

# Use Case

The dependable processing of live data streams at the network edge presents many possibilities for IoT applications.
For example, @Rocha:2021 recognise the need for Smart Home solutions that are designed for people with disability and mobility needs in order to provide independent *assisted living*.
This is accomplished through sensors that trigger events with minimal or unconventional means of interaction by the end user, such as through voice, eye movement, bespoke GUIs/controllers, or simply human presence.
Actuators, such as plugs, locks, kitchen appliances, and alarms, can trigger because of this minimal human input.

Assisted living can leverage low-latency event detection and actuation from `BoboCEP` to ensure a reliable and rapid response to events.
For example, if an elderly resident were to fall in their home and require an ambulance, then this 'phenomenon' could be detected through one-or-more different patterns of correlated, temporal data.
The patterns may be:

1. A person is detected entering a room and they have not been detected moving for at least `30` seconds, nor detected leaving the room, nor any indication through some other modality (e.g., microphone, interaction with home appliances).
2. An attached heart-rate sensor has stopped providing data or has been consistently reporting dangerously low readings.
3. Calls for help are heard via the microphone or a virtual assistant system.

On fulfilment of the phenomenon via any pattern, a complex event is generated and an action may be triggered to:

- Call for an ambulance.
- Notify neighbours.
- Unlock the front door.

Furthermore, @Scattone:2021 cite `BoboCEP` as a relevant technology even in the context of large-scale solutions, such as Smart Cities, where `BoboCEP` may only send events of high importance to the cloud.
Indeed, the assisted living scenario is directly applicable: most data can stay privately within the home network (e.g., heart-rate data, location of people in their homes), but calling for an ambulance and notifying neighbours can leverage cloud services.

Due to the critical nature of assisted living, `BoboCEP` may run in a distributed manner over multiple devices/software instances.
This mode uses active replication to maintain consistent state over each instance so that, if one instance fails, then detecting and reporting phenomena would not be impeded.
This design provides the additional benefit of being able to load-balance data across all instances, which helps to scale to a vast number of sensors and actuators.

# Acknowledgements

I acknowledge contributions from Dr Gerald Kotonya for assisting in the design of `BoboCEP` in its earlier versions, helping to shape the project into what it has become.

# References
