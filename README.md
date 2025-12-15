# Pathik AI - Full-Stack Marketing Campaign Manager

A full-stack application that allows users to create marketing campaigns locally and publish them to Google Ads as inactive (paused) campaigns.

This project is built as part of the Pathik AI Full-Stack Assignment using React, Flask, PostgreSQL, and the Google Ads API.

## Features

- Create marketing campaigns and store them locally (DRAFT)
- Persist campaign data in PostgreSQL
- Publish campaigns to a real Google Ads account
- Campaigns are created PAUSED to avoid accidental billing
- Store Google Campaign ID after publishing
- Pause (disable) published campaigns
- Simple and functional UI
- Fully Dockerized setup

## Tech Stack

### Frontend

- React (Create React App)
- Fetch API
- Plain CSS

### Backend

- Python 3
- Flask
- SQLAlchemy
- Flask-Migrate
- PostgreSQL
- Google Ads API (official client)

### Infrastructure

- Docker
- Docker Compose

## Environment Variables

Create a `.env` file at the project root:

```env
DATABASE_URL=postgresql://pathik:pathik@db:5432/pathik

GOOGLE_ADS_DEVELOPER_TOKEN=
GOOGLE_ADS_CLIENT_ID=
GOOGLE_ADS_CLIENT_SECRET=
GOOGLE_ADS_REFRESH_TOKEN=

# MCC (manager account ID)
GOOGLE_ADS_LOGIN_CUSTOMER_ID=

# Client account ID
GOOGLE_ADS_CUSTOMER_ID=
```
A sample is provided in ``.env.example``.

## Running the Application (Docker)

### Prerequisites

- Docker
- Docker Compose

### Start Services
```
docker compose up –build -d
```
### Initialize Database 
- This applies the database schema using Flask-Migrate and must be run once on first startup.
```
docker compose run backend flask db upgrade
```
## Access the App

> Frontend: http://localhost:3000  
> Backend API: http://localhost:5001/api

## Frontend Overview

The user interface includes a tab-based layout for creating and viewing campaigns.

Key features include:

- Controlled form inputs for campaign creation
- Loading and error states
- Campaign status badges (DRAFT, PUBLISHED)
- Publish and Pause actions

## Backend Overview

The backend follows a service-layer architecture:

- Application Factory Pattern for initializing the app
- Routes handle HTTP requests
- Services handle business logic and Google Ads integration
- Models are SQLAlchemy models for database persistence

## API Endpoints

### Create Campaign (Local Only)

POST ``/api/campaigns``

Creates a campaign in PostgreSQL with status DRAFT.

### Get Campaigns

GET ``/api/campaigns``

Returns all locally stored campaigns.

### Publish Campaign to Google Ads

POST ``/api/campaigns/{id}/publish``

Creates campaign budget.  
Creates Google Ads campaign (PAUSED).  
Creates ad group and ad.  
Stores Google Campaign ID.  
Updates status to PUBLISHED.

### Pause Campaign

POST ``/api/campaigns/{id}/pause``

Pauses a published Google Ads campaign.

## Google Ads Setup

To enable publishing, ensure you have:

- Created a Google Ads account
- Developer Token
- Created OAuth credentials (Client ID & Secret)
- Generated a Refresh Token
- Set all required environment variables

Refer to the official documentation:  
https://developers.google.com/google-ads/api

## Design and Scalability Notes

- Draft-first campaign lifecycle with local persistence in PostgreSQL  
  (campaigns are created and stored locally before any external API calls)

- Safe Google Ads publishing workflow  
  (campaigns, ad groups, and ads are created in PAUSED state to prevent billing)

- Layered backend architecture  
  (routes → services → models → external integrations)

- Fully containerized development and runtime environment  
  (frontend, backend, and database orchestrated via Docker Compose)

### Future Extensions

- Support for additional Google Ads campaign types using the existing service layer  
  (e.g. Display or Video campaigns via new service implementations)
  
- Validation of creative assets before publishing  
  (URL reachability, basic format checks, required fields)

- Asynchronous publishing using background workers  
  to prevent long-running Google Ads API calls from blocking HTTP requests

- Retry and reconciliation logic for partial Google Ads failures  
  (e.g. campaign created but ad group failed)

- Pagination and filtering for campaign listings  
  (to avoid returning all campaigns at once as the dataset grows)

- User-level authentication and account scoping  
  to associate campaigns with individual users or Google Ads accounts
