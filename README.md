# Sample Webhooks Consumer

## Introduction

This repository is meant to provide a sample Axon webhooks consumer using an async processing architecture.

## Intended purpose

The consumer is designed to show how a developer would implement:

- An HTTP POST endpoint to receive data
- Authentication using HMAC
- An async "processor" that consumes a webhook payload and performs actions with it
- Reading evidence metadata from the Axon Partner API
- Syncing evidence metadata with a "local" copy of evidence

## Requirements

In order to run the code in this repository, you must have the following on your computer:
- Python 3.10 or higher
- The Python tool [Pipenv](https://pipenv.pypa.io/en/latest/#install-pipenv-today)
- Docker and docker-compose
- A method to expose an https endpoint on your computer to the internet, such as [ngrok](https://ngrok.com/)

## Configuring credentials

### Axon Partner API

1. Configure an API Client using the Partner API Guide
2. In this repository, open `credentials.py`
3. Place the API Client credentials in the relevant fields under `API_CREDENTIALS`
4. Place the domain of your evidence.com agency under `API_DOMAIN`

### Webhooks Secrets
1. Come up with a secret keyto sign webhooks with. This must be longer then 20 characters.
2. Place this secret in `credentials.py` under the variable `WEBHOOK_HMAC_SECRET`.

### Start an ingress

The HTTP endpoint this project sets up will need to be accessible from the internet. It will
need to use HTTPS with a signed, valid cert. For development purposes, you can use [ngrok](https://ngrok.com/).

Create an account and follow the instructions on their site to install their client and configure it
with your new account credentials. Then, run: `ngrok http 8080`.

## Configure a Webhook

Follow the Webhooks API Developer's guide to configure a webhook. [TBD]

## Starting the whole project

The receiver and worker must both run at the same time, with each running in its
own terminal window.

Prerequisites:

1. From the root of this repository, run `pipenv install`, then `pipenv shell`
2. Run `docker-compose up -d` to start the redis instance

### Start the Webhook Receiver
1. From the root of this repository, run `pipenv shell`
2. Run `flask --app receiver run --port 8080` to start the receiver on port `8080`

### Start the Worker
1. From the root of this repository, run `pipenv shell`
2. Run `rq worker` 
