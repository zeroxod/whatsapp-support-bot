# WhatsApp Support Bot

A Python-based WhatsApp customer support bot using the official
Meta WhatsApp Cloud API.

## Features

- Automated customer replies
- Product information
- Order enquiries
- Delivery information
- Payment information
- Business hours
- Human support option

## Requirements

- Python 3.10+
- Meta Developer account
- WhatsApp Cloud API access
- Render account
- GitHub account

## Installation

Install dependencies:

pip install -r requirements.txt

## Run locally

gunicorn app:app

## Deployment

Deploy this repository as a Web Service on Render.

Build command:

pip install -r requirements.txt

Start command:

gunicorn app:app

## Environment Variables

Configure your credentials in Render's Environment
section. See `.env.example` for the required variable names.

## Webhook

Callback URL:

https://YOUR-RENDER-SERVICE.onrender.com/webhook

Subscribe to the WhatsApp `messages` webhook field.
