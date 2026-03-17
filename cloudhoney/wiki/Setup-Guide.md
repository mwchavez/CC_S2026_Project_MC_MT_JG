# Setup Guide

Step-by-step instructions for deploying and configuring each CloudHoney component.

## Prerequisites

- GCP account with billing enabled
- Project `cloudhoney-sp26` created with required APIs enabled
- Python 3.11+
- Git

## 1. GCP Project Setup

> See [Architecture > IAM](Architecture#iam) for role assignments and service account configuration.

## 2. Honeypot Deployment

> TODO: Document VM provisioning, firewall rules, Flask app deployment, systemd configuration

## 3. Cloud Logging & Storage Pipeline

> TODO: Document log sink creation, GCS bucket configuration, log schema

## 4. Traffic Generator

> TODO: Document how to run each attack scenario

## 5. Cloud Functions Deployment

> TODO: Document function deployment, Pub/Sub topic setup, Firestore initialization

## 6. Alert Delivery

> TODO: Document SendGrid setup, Secret Manager configuration, alert function deployment

## 7. Dashboard Deployment

> TODO: Document containerization, Cloud Run deployment, public URL configuration
