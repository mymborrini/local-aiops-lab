# What I have created

The main goal is to develop an application and practice with observability integrated with AI

Our application has different elements:

 - app
 - outbox_processor
 - job_processor
 - redis
 - postgresql

## App

Is the flask application, it exposes endpoints to create and read job. The main goal is to save the job on postgres in PENDING state

## Outbox processor

Is the service responsible to fetch all the job in PENDING state and save them in the *jobs* redis queue

## Job processor

Is the service responsible to 
 - get the last job from redis
 - set the job in RUNNIG state
 - make all the necessary operations
 - set the job in COMPLETED state or in FAILED state
 - manage the retry in case of FAILED