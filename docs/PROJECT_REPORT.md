# Project Report — Real-Time Cloud-Based Event Planning & RSVP Tracker

## Abstract
This project implements a cloud-oriented event planning and RSVP platform using React, FastAPI, PostgreSQL, JWT authentication, RBAC and WebSockets. It provides centralized event management, attendee responses, analytics, notifications and concurrency-safe capacity handling.

## Problem Statement
Manual RSVP tracking can produce duplicate responses, stale attendance counts and difficult coordination. A centralized cloud application gives organizers and attendees a shared source of truth accessible from different devices.

## Objectives
- Demonstrate managed cloud database usage.
- Implement secure authentication and role authorization.
- Expose REST APIs.
- Demonstrate genuine real-time updates.
- Handle capacity and concurrent RSVP requests safely.
- Provide analytics, notifications and waitlist behavior.
- Produce GitHub-ready proof of work.

## Architecture
React communicates with FastAPI over HTTPS. FastAPI validates JWT identity and role permissions, executes transactional PostgreSQL operations, and broadcasts committed RSVP analytics over WebSockets. Supabase PostgreSQL can be used as the managed cloud database.

## Key technical contribution
Capacity is protected by a PostgreSQL transaction with a row lock on the event. This prevents two simultaneous final-seat requests from both succeeding.

## Security
Passwords are Argon2-hashed, JWTs protect APIs, RBAC controls privileged operations, Pydantic validates inputs, unique database constraints prevent duplicate RSVP rows, and secrets are stored in environment variables.

## Testing
The repository includes automated unit checks and a verification matrix covering registration, authorization, event management, RSVP changes, deadline/capacity enforcement, waitlist promotion, notifications, real-time delivery, analytics and failure handling.

## Conclusion
The project demonstrates how a conventional event application can be structured as a cloud computing system with managed database services, stateless APIs, real-time communication, secure access control and scalable deployment patterns.
