Overview
========

Purpose
-------


It's easiest to describe The MozDef Event Framework as a set of micro-services you can use to integrate event sources with the `Mozilla Enterprise Defense platform <https://mozdef.readthedocs.io/en/latest/>` (MozDef).

Provides
--------

Many sources are not wholly contained within the datacenter, there are SAAS and IAAS providers which may provide events that are external to the network. Exposing your security infrastructure doesn't ensure a secure pipeline. In order to solve for this we decided on pulling that information in as our method of choice.
Utilizing cloud based microservices can reduce exposure, ensure efficiency and scalability, and leads to less maintenance. We created a framework using cloudformation and serverless to build a pipeline that will allow placement of lambda scripts specific for an event source and provide continuous deployment and integration.
This takes the guesswork out of having to write serverless and cloudformation code every time  you want to deploy a pipeline for a new event source and creates a standard method to be used to obtain those events. Webhook sources utilize an AWS API gateway that they can post events to. As we scale this out the capabilities will increase.
The hope is to have a scalable framework that can be deployed for both rest and webhook based sources.

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


   * AWS API Gateway
   * AWS Cloudformation
   * AWS CloudWatch
   * AWS CodePipeline
   * AWS CodeCommit
   * AWS CodeBuild
   * AWS Lambda
   * AWS S3
   * AWS SQS
   * AWS XRay
   * GitHub
   * Serverless framework

Status
------

The MozDef event framework is under development at this time.

Roadmap
-------

Done
****

   * Allows the use of Webhook API connectivity
   * Can pull configuration from one or more sources (Github/CodeCommit) during build by selecting the appropriate CF template
   * Utilizes ssm/keystore parameters to prevent exposure of secrets
   * CI/CD pipeline is implemented using AWS Codepipeline

ToDo
****

   * Implement Dead Letter Queue (DLQ) reprocessing functionality
   * Implement schema validation
   * Implement function library to allow choice between webhook API or rEST API connectivity
