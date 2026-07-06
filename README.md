# Hospital AI Voice Appointment Booking Agent

An end to end voice powered appointment booking system for a hospital, combining a conversational AI voice agent with a lightweight admin dashboard.

## Overview

This project lets patients book, cancel, and check appointments through natural voice conversation, without filling out forms or waiting on hold. A staff facing Streamlit dashboard mirrors the same backend for manual booking, oversight, and testing.

## Features

- Voice based booking: patients speak naturally to schedule or cancel appointments, powered by Vapi
- Appointment scheduling and cancellation: a full booking flow with conflict safe scheduling
- Doctor availability lookup: check which doctors are free on a given day, with working hour and time slot logic
- Admin dashboard: a Streamlit interface for manual scheduling, cancellations, and viewing the day's appointments
- FastAPI backend: a clean REST API layer backed by SQLite through SQLAlchemy

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend API | FastAPI, SQLAlchemy, SQLite |
| Frontend | Streamlit |
| Voice Agent | Vapi |
| Tunneling | ngrok |
| Language | Python |

## Architecture

Caller -> Vapi (voice agent) -> ngrok tunnel -> FastAPI backend -> SQLite
                                                       |
                                          Streamlit admin dashboard

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /schedule_appointment/ | Book a new appointment |
| POST | /cancel_appointment/ | Cancel an existing appointment |
| GET | /list_appointments/ | View appointments for a given date |
| GET | /list_doctors/ | List all doctors and their working hours |
| GET | /check_availability/ | Check a doctor's open slots on a given date |

## Doctors and Availability

The system currently supports the following doctors, each with a fixed weekly schedule. Availability is calculated automatically by checking each doctor's working days and hours against existing bookings.

| Doctor | Specialty | Working Days | Hours |
|--------|-----------|---------------|-------|
| Dr. Ali Raza | General Physician | Monday to Friday | 09:00 to 17:00 |
| Dr. Sara Khan | Cardiologist | Monday, Wednesday, Friday | 10:00 to 15:00 |

Appointment slots are calculated in 30 minute increments within each doctor's working hours. A slot is considered available if it falls within the doctor's schedule and has not already been booked for that date.

New doctors can be added directly in the database seeding logic, allowing the schedule to scale as the hospital grows.

## Running Locally

Install dependencies:

uv sync

or

pip install -r requirements.txt

Initialize the database:

uv run database.py

Start the backend:

uv run backend.py

In a separate terminal, start the dashboard:

streamlit run mainpage.py

Expose the backend for Vapi in a separate terminal:

ngrok http 4444

Update the ngrok HTTPS URL in your Vapi tool configurations and in the Streamlit Backend URL field after each restart, since free ngrok URLs change on every run.

## Project Status

Actively developed. Currently supports single hospital scheduling with optional doctor assignment, working hours validation, and time slot conflict checks.

## License and Usage

All rights reserved. This project and its source code are shared for portfolio and demonstration purposes only. No part of this codebase may be copied, modified, distributed, or used in any form, commercial or non commercial, without explicit written permission from the author.

## Author

Built by Affan Bhat
GitHub: devAffaan
