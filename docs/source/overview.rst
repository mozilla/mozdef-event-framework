Overview
========

Purpose
-----
It's easiest to describe The MozDef Event Framework as a set of micro-services you can use as to integrate event sources with the [Mozilla Enterprise Defense platfrorm](https://mozdef.readthedocs.io/en/latest/) (MozDef).

Provides
----

Many sources are not wholly contained within the datacenter, there are SAAS and IAAS providers which may provide events that are external to the platform. This requires some architecing of a new pipeline to get those events into MozDef.
Utilizing cloud based microservices can ensure efficiency and scalability and leads to less maintenance. We created a framework using cloudformation and serverless to build a pipeline that will allow placement of lambda scripts specific for an event source and provide co
This takes the guesswork out of having to write serverless and cloudformation code every time  you want to deploy a pipeline for a new event source and creates a standard method to be used to obtain those events.

Goals
-----

High level
**********

* Provide a platform for use by security infrastructure engineers to rapidly deploy a pipeline to enable ingestion of events into MozDef.
* Facilitate continuous integration and development.
* Facilitate repeatable, predictable processes for adding new event sources.
* Provide a means with which to reprocess any events that do not meet the requirements you set.

Technical
*********

* Offer micro services that enable rapid consumption of various event sources as needed.
* Scalable, should be able to handle thousands of events per second, provide validation, and a means to reprocess events that fail validation by utilizing the CI/CD pipeline this framework builds.

Architecture
------------
The following components make up this framework:


   * CodePipeline
   * CodeCommit
   * CodeBuild
   * s3
   * CloudWatch
   * GitHub.


Status
------

The MozDef event framework is under development at this time.
