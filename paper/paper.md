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

affiliations:
 - name: Department of Computer Science, University of Bath, United Kingdom

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
For example, a developer considers what *phenomena* they would like `BoboCEP` to be able to detect, and denotes one or more *patterns* that must emerge in the data stream that, if fulfilled by the relevant data, would infer the existence of a given phenomenon.
On pattern fulfilment, an action may be executed.
The data stream represents properties from various Things, the fulfillment of a pattern represents event detection, and the action affordance is applicable on event detection.

# Statement of Need

`BoboCEP` has existed for several years as a CEP engine to provide inferential reasoning and decision-making on streaming data [@Power:2020] and has continually been developed ever since to become a robust platform on which to deploy IoT systems.
It adopts an *information flow processing* (IFP) architecture that consumes a data stream from diverse sources (i.e., Things) [@Cugola:2012].
These data enter the system in a serialised and uncorrelated manner (i.e., *simple* events), which are then compared against user-designed *patterns* that seek to recognise temporal relationships.
If data satisfies its conditions, then a *complex* event is generated and an action may be executed consequently.

Unlike other CEP systems, which focus on cloud-based big data platforms [@Giatrakos:2020], `BoboCEP` is designed for dependable edge computing in IoT systems by extending the IFP architecture to additionally provide *fault tolerance* (FT) via the active replication of partially-completed complex events across multiple instances of the software.
That is, it can be deployed on $n$ devices across the network edge and is able to protect the system against, at most, $n-1$ software failures.
This is crucial to ensure that valuable insights into patterns emerging across the ever-changing cyber-physical environment are not missed, leading to events not being recognised and necessary actions not triggering.

# Acknowledgements

I acknowledge contributions from Dr Gerald Kotonya for assisting in the design of `BoboCEP` in its earlier versions, helping to shape the project into what it has become.

# References
