Overview
========

Purpose
-------

It's easiest to describe The MozDef Event Framework as a set of micro-services you can use to integrate event sources with the `Mozilla Enterprise Defense platform <https://mozdef.readthedocs.io/en/latest/>`_ (MozDef).

Provides
--------

Many resources are not wholly contained within the datacenter, there are SAAS and IAAS providers which may provide event logging that is external to the network where your SIEM resides. 
Exposing your security infrastructure doesn't ensure a secure pipeline. In order to solve for this we decided on pulling that information as our method of choice, as opposed to pushing.
Utilizing cloud based microservices can reduce exposure, ensure efficiency and scalability, and leads to less maintenance.

We created a framework using AWS Cloudformation and the Serverless framework to build a pipeline that will allow placement of lambda scripts specific for an event source and provide continuous deployment and integration.
This takes the guesswork out of having to write serverless and cloudformation code every time  you want to deploy a pipeline for a new event source and creates a standard method to be used to obtain those events. 

Webhook sources utilize an AWS API gateway that they can post events to. As we scale this out the capabilities will increase.
The hope is to have a scalable framework that can be deployed for both REST and webhook based sources.

Flow
----

There are There cloudformation templates to choose from in the templates directory:

* Github repo used as source: templates/codepipeline-cf-template-github-source.yml
* CodeCommit repo used as the config source: templates/codepipeline-cf-template-codecommit-source.yml
* Github and CodeCommit used as a multiple source that can be merged: templates/multi_source_template/codepipeline-cf-template-with-merge.yml

We've added toggles to view the basic workflow diagrams below, feel free to choose what works best for you.

Workflow Diagrams
*****************

.. toggle-header::
    :header: **1. Using a Single Source Repo:**

      Workflow using a Single Source Repo Cloudformation Template

      .. image:: images/MozDef-Event-Framework_process_flow_single-source.png
         :width: 600
         :alt: High Level Overview of the Work/Process Flow Steps From Start to Finish


.. toggle-header::
    :header: **2. Using Multiple Source Repos:**

      Workflow using the Mutliple Source Repos w/ Merge Cloudformation Template

      .. image:: images/MozDef-Event-Framework_process_flow_multi-source.png
         :width: 600
         :alt: High Level Overview of the Work/Process Flow Steps From Start to Finish

|
Dataflow Diagram
*****************

.. toggle-header::
    :header: **Serverless Components and Data Flow:**

      Example Dataflow using Zoom's Webhook

      .. image:: images/mozdef_event_framework_dataflow.png
         :width: 600
         :alt: High Level Overview of the Work/Process Flow Steps From Start to Finish

|
Components
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

Roadmap
-------

Done
****

   * Allows the use of Webhook API connectivity
   * Can pull configuration from one or more sources (Github/CodeCommit) during build by selecting the appropriate CF template
   * Utilizes SSM and Secrets manager parameters to prevent exposure of secrets through code
   * CI/CD pipeline is implemented using AWS Codepipeline

ToDo
****

   * Implement Dead Letter Queue (DLQ) reprocessing functionality
   * Implement schema validation
   * Implement function library to allow choice between webhook API or REST API connectivity
   * Implement monitoring of the entire stack that is created by this framework

Inspiration
-----------
The following resources inspired us and were used to build out this project:

* https://github.com/tooltwist/codepipeline-artifact-munge
* https://github.com/getcft/aws-serverless-code-pipeline-cf-template

