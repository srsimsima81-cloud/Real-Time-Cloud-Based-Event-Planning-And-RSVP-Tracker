# Real-Time Cloud-Based Event Planning & RSVP Tracker

A student-focused cloud computing project demonstrating managed PostgreSQL, JWT authentication, RBAC, REST APIs, transactional RSVP/capacity handling, waitlists, in-app notifications, analytics and WebSocket-based real-time dashboard updates.

## 1. What this project demonstrates

**Simple explanation:** organizers publish events; attendees discover them and respond Going/Maybe/Not Going; PostgreSQL is the central source of truth; FastAPI validates and stores changes; WebSockets push updated analytics to connected dashboards without a manual refresh.

**Technical flow:** Organizer → FastAPI REST API → PostgreSQL/Supabase PostgreSQL → RSVP transaction → WebSocket broadcast → Organizer dashboard.

## 2. Fixed technology stack

- Frontend: React + Vite
- Backend: Python + FastAPI
- Database: PostgreSQL; compatible with Supabase PostgreSQL
- Authentication: JWT
- Authorization: RBAC
- Real-time: FastAPI WebSockets
- Object storage: Supabase Storage/S3 can be added only for future event assets; this core build does not need file storage
- Containerization: Docker / Docker Compose
- Source control: Git/GitHub

## 3. Cloud concepts mapped to the project

| Concept | Where it appears |
|---|---|
| Cloud computing | Hosted React/FastAPI + managed PostgreSQL architecture |
| SaaS | Browser-accessible event application |
| PaaS | Supabase PostgreSQL / student-friendly app hosting |
| IaaS | Optional VM/container host; not required in the core deployment |
| Cloud database | Supabase PostgreSQL is a managed cloud PostgreSQL option |
| Authentication | JWT login/register |
| Authorization/RBAC | Attendee, Organizer, Admin roles |
| REST API | FastAPI endpoints |
| WebSockets | Live RSVP analytics |
| Serverless | Optional deployment alternative; not required |
| Event-driven architecture | RSVP/announcement changes trigger notifications and WebSocket broadcasts |
| Cloud functions | Optional future trigger implementation |
| Scalability | Stateless API, managed DB, horizontal app replicas |
| Elasticity | Scale frontend/backend independently on a suitable host |
| High availability | Managed DB + multiple API replicas in production |
| Load balancing | Place a managed load balancer in front of replicated FastAPI instances |
| CDN | Static React assets can be served by a CDN-enabled host |
| Caching | Optional event-list caching for high traffic |
| Secrets | `.env` locally; platform secret store in cloud |
| Logging/monitoring | FastAPI/Uvicorn logs + host/DB monitoring |
| Backup | Managed PostgreSQL backups/Supabase backups |
| CI/CD | GitHub Actions can run tests/builds before deployment |

## 4. Why real-time matters

Real-time means connected clients receive important state changes as they happen. When Attendee A changes to GOING, the API commits the RSVP and broadcasts the new analytics through WebSocket. The organizer dashboard updates immediately. Polling is simpler but can be delayed; Server-Sent Events are one-way server-to-browser streams; WebSockets support two-way persistent communication and are used here.

## 5. Folder structure

- `frontend/` React UI, components, pages, API client and styling
- `backend/app/` FastAPI application
- `backend/app/models/` SQLAlchemy data models
- `backend/app/api/` authentication, event, RSVP and notification routes
- `backend/app/services/` analytics, notifications and WebSocket connection manager
- `backend/app/ws/` WebSocket endpoint
- `backend/tests/` automated tests
- `backend/schema.sql` reference PostgreSQL schema
- `backend/seed.py` fictional demo data
- `docs/` report/supporting documentation
- `screenshots/` place final submission screenshots here
- `reports/` place exported project report here

## 6. Windows prerequisites

Install:
1. Python 3.13+
2. Node.js 22+
3. PostgreSQL 16+ OR Docker Desktop
4. Git

### Option A: Docker (recommended for local setup)

From the project root:

```powershell
docker compose up -d --build
```

Seed demo data:

```powershell
docker compose exec backend python seed.py
```

Open:
- Frontend: http://localhost:5173
- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

### Option B: PostgreSQL installed locally

Create a database named `event_rsvp`, then:

```powershell
cd backend
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python seed.py
uvicorn app.main:app --reload --port 8000
```

In another PowerShell window:

```powershell
cd frontend
npm install
copy .env.example .env
npm run dev
```

Open http://localhost:5173.

## 7. Supabase cloud database setup

1. Create a free Supabase project.
2. Open the project's PostgreSQL connection settings.
3. Copy a connection string suitable for asyncpg and set `DATABASE_URL` in `backend/.env`.
4. Set a strong `JWT_SECRET` and `CORS_ORIGINS` to the deployed frontend URL.
5. Start the FastAPI backend. The current educational build creates tables automatically at startup. For a production project, migrate to Alembic migrations before schema changes.
6. Supabase PostgreSQL remains the cloud source of truth; real-time delivery is handled by the FastAPI WebSocket service in this build.

## 8. Demo accounts

All are fictional:

- Organizer: `organizer@demo.com` / `Organizer@123`
- Attendee A: `attendee1@demo.com` / `Attendee@123`
- Attendee B: `attendee2@demo.com` / `Attendee@123`
- Attendee C: `attendee3@demo.com` / `Attendee@123`

## 9. Demo workflow

1. Login as organizer.
2. Open Dashboard and create **Cloud Computing Workshop**, capacity 100.
3. Open a second browser/incognito window and login as Attendee A.
4. Open Events → select the workshop → Going.
5. Return to organizer dashboard: the live Going count changes without manual refresh.
6. Login as Attendee B in a third window → Maybe.
7. Change B to Going; organizer analytics update again.
8. Organizer publishes an announcement; RSVP users receive an in-app notification.
9. Test capacity by creating a small-capacity event and using multiple demo accounts.
10. Cancel a Going RSVP to exercise waitlist promotion.
11. Attempt to edit another organizer's event through the API; expect HTTP 403.

## 10. REST API inventory

### Auth
- `POST /api/register` — create user and return JWT
- `POST /api/login` — authenticate and return JWT
- `POST /api/logout` — client-side token discard acknowledgement
- `GET /api/me` — current authenticated user

### Events
- `POST /api/events` — Organizer/Admin only
- `GET /api/events` — published/full events
- `GET /api/events/upcoming` — upcoming published/full events
- `GET /api/events/{id}` — event details
- `PUT /api/events/{id}` — owner/Admin only
- `DELETE /api/events/{id}` — owner/Admin only
- `POST /api/events/{id}/cancel` — owner/Admin only
- `POST /api/events/{id}/announcements` — owner/Admin only
- `GET /api/events/{id}/announcements` — authenticated/public-read route

### RSVP
- `POST /api/events/{id}/rsvp` — create/update response
- `PUT /api/events/{id}/rsvp` — update response
- `DELETE /api/events/{id}/rsvp` — cancel response
- `GET /api/events/{id}/rsvps` — owner/Admin only
- `GET /api/rsvps/me` — current user's RSVPs
- `GET /api/events/{id}/analytics` — owner/Admin only

### Notifications
- `GET /api/notifications`
- `PUT /api/notifications/{id}/read`

Interactive API documentation is available at `/docs`.

## 11. Capacity and race-condition design

A naive implementation does `if currentGoing < capacity` and then inserts an RSVP. Two concurrent requests can both observe 99/100 and both insert. This creates 101 Going users.

This project instead starts a database transaction and locks the event row with PostgreSQL `SELECT ... FOR UPDATE`. The Going count is checked while the event row is locked. Only one transaction can make the final-seat decision at a time. A full event sends later Going requests to the waitlist. This is the key concurrency proof-of-work feature.

## 12. Waitlist

Waitlist entries are stored with `joined_at`. Promotion uses FIFO ordering and locks the candidate row. When a Going attendee cancels, the first waiting user is promoted and receives a notification.

## 13. Security

- JWT authentication
- Password hashing with Argon2 via `pwdlib`
- RBAC checks in backend routes
- Owner checks on organizer operations
- Pydantic validation
- Database unique constraint `(event_id,user_id)` prevents duplicate RSVP rows
- Backend/database is the source of truth; the frontend cannot directly change counts
- CORS is explicitly configured
- Secrets are environment variables, never committed
- HTTPS should be enabled by the deployment platform
- PostgreSQL/Supabase provides encryption at rest/in transit controls at the service level
- Production deployments should add rate limiting and centralized secret management
- Audit-log table is included for production extension

## 14. Failure handling

- Database failures surface as API errors and should be monitored by the host.
- Transaction rollback protects partial RSVP updates.
- Duplicate RSVP requests are safe because of the unique constraint and upsert-like update behavior.
- WebSocket clients should reconnect after network failure; the next page/API load restores current state.
- Notification failure should not be allowed to corrupt the RSVP transaction in a production queue-based version.
- User refreshes do not change the database state; the API reloads the authoritative RSVP state.

## 15. Testing

Run:

```powershell
cd backend
pytest -q
```

Core automated checks include analytics math and endpoint inventory. For a production extension, add a dedicated PostgreSQL test database and run full HTTP integration tests for all 25 scenarios below.

### Verification matrix

| ID | Scenario | Expected result |
|---|---|---|
| T01 | Register new user | 201 + JWT |
| T02 | Duplicate registration | 409 |
| T03 | Login | 200 + JWT |
| T04 | Organizer creates event | 201 |
| T05 | Attendee creates event | 403 |
| T06 | Event retrieval | 200 |
| T07 | Valid RSVP | 200/201 + stored row |
| T08 | Duplicate RSVP | Same unique user/event record, no duplicate |
| T09 | GOING → MAYBE | Count moves from Going to Maybe |
| T10 | MAYBE → GOING | Count moves back |
| T11 | Cancel RSVP | NOT_GOING and possible promotion |
| T12 | Deadline passed | 409 |
| T13 | Capacity reached | Going rejected/waitlisted |
| T14 | Simultaneous final-seat requests | At most one final seat; other request waitlisted |
| T15 | Waitlist promotion | FIFO candidate promoted |
| T16 | Announcement | Stored + notifications |
| T17 | Notification generation | User sees notification |
| T18 | Unauthorized event edit | 403 |
| T19 | Unauthorized RSVP access | Backend prevents cross-user modification |
| T20 | WebSocket update | Organizer receives analytics event |
| T21 | Analytics | Counts and percentages match DB |
| T22 | DB failure | API returns error; transaction does not partially commit |
| T23 | WebSocket disconnect | Client can reconnect; DB state remains authoritative |
| T24 | Expired JWT | 401 |
| T25 | Event cancellation | Status CANCELLED + notifications |

## 16. Local real-time simulation

Use three browser windows:

- Window 1: Organizer account
- Window 2: Attendee A
- Window 3: Attendee B

With the organizer analytics page open, change A to GOING. The organizer count becomes 1. Change B to GOING. It becomes 2. Change A to MAYBE. Going becomes 1 and Maybe becomes 1. No organizer refresh is required.

## 17. Cloud deployment approach A — student-friendly

Recommended architecture:

`Browser → Static React host/CDN → FastAPI host → Supabase PostgreSQL`

WebSocket connection:

`Browser ↔ FastAPI WebSocket service`

Suggested process:
1. Push repository to GitHub.
2. Create Supabase project and set the database URL as a deployment secret.
3. Build/deploy FastAPI with the included `backend/Dockerfile` on a student-friendly container-capable host.
4. Build/deploy React with `VITE_API_URL` set to the public API URL.
5. Set CORS to the deployed frontend URL.
6. Seed demo data once from a secure environment.
7. Verify `/health`, login, event creation, RSVP and WebSocket behavior.

No paid AWS infrastructure is required for the core project.

## 18. Enterprise reference architecture

`Users → CloudFront/CDN → React hosting → API Gateway/Load Balancer → FastAPI/Lambda → PostgreSQL/RDS → notification service`

For AWS, Cognito can replace the custom JWT identity layer, RDS can provide PostgreSQL, API Gateway WebSocket can provide managed real-time delivery, SES/SNS can provide email/notifications, and CloudWatch can provide monitoring. These are architectural extensions, not dependencies of this student build.

Azure equivalents include Static Web Apps, Container Apps/App Service, Azure Database for PostgreSQL, Entra ID, API Management/Web PubSub and Monitor. GCP equivalents include Cloud Storage/Firebase Hosting, Cloud Run, Cloud SQL PostgreSQL, Identity Platform, and managed monitoring.

## 19. Scalability discussion

For 100 users, one FastAPI instance and managed PostgreSQL are sufficient for a demonstration. For 10,000 users, run multiple stateless API instances behind a load balancer, add indexes and cache read-heavy event lists. For 1,000,000 users or a major RSVP spike, use autoscaling/serverless compute, a managed PostgreSQL tier sized for concurrency, a queue for notifications, caching, rate limiting, CDN delivery and a shared real-time broker/service so WebSocket messages work across replicas.

A single event can become a database hotspot because many requests update the same capacity state. Keep transactions short, lock only the necessary event row, index RSVP lookup columns, avoid repeated full-table scans, and consider a queue/partitioning strategy for very large systems.

## 20. Cloud architecture text diagram

```text
 Attendee / Organizer Browsers
          │
          ├── HTTPS REST ───────────────┐
          │                             ▼
          │                       FastAPI API
          │                    Auth + RBAC + Validation
          │                             │
          │                             ▼
          │                     PostgreSQL/Supabase
          │                      ▲       │
          │                      │       │
          └── WebSocket ◄────────┴───────┘
                         RSVP broadcast

 Optional production services:
 CDN → React static assets
 Queue → notification processing
 Monitoring → API/DB/WebSocket metrics
 Object storage → event images/files if required
```

## 21. Expected Output and Verification

- **Registration/Login:** authenticated user reaches the dashboard; invalid credentials show an error.
- **RBAC:** attendee sees attendee workflow; organizer sees organizer controls; cross-owner event edits return 403.
- **Event creation:** new event appears in the event list with date, venue, capacity and status.
- **Event details:** event information and RSVP controls are visible.
- **RSVP:** confirmation appears and the response is stored in PostgreSQL.
- **Real-time:** organizer analytics update in another browser without a manual refresh.
- **Capacity:** final seat is accepted once; concurrent/next Going request is waitlisted.
- **Waitlist:** cancellation frees a seat and the earliest waiting user is promoted.
- **Announcement:** organizer publishes a message and RSVP users receive an in-app notification.
- **Analytics:** Going/Maybe/Not Going, available seats, response rate and capacity utilization match stored data.
- **Cloud database:** replacing local `DATABASE_URL` with the Supabase PostgreSQL URL moves the source of truth to the managed cloud database.
- **Health:** `/health` returns `status=ok` and `database=connected`.

## 22. Recommended screenshots for submission

1. Login/registration page
2. Organizer dashboard with live analytics
3. Event creation form
4. Published event listing
5. Event details with RSVP buttons
6. Attendee dashboard/My RSVPs
7. Two-window real-time RSVP demonstration
8. Capacity full + waitlist behavior
9. Announcement/notification view
10. API Swagger `/docs`
11. Supabase PostgreSQL table/schema view (with only fictional data)
12. Project cloud architecture diagram
13. GitHub repository structure
14. Test output (`pytest -q`)
15. Final deployed application home/dashboard

## 23. GitHub strategy

Suggested repository name: `real-time-cloud-event-rsvp-tracker`

Commit sequence:
1. `init: project architecture and documentation`
2. `feat: FastAPI authentication and RBAC`
3. `feat: PostgreSQL event and RSVP models`
4. `feat: capacity-safe waitlist logic`
5. `feat: WebSocket live analytics`
6. `feat: React dashboards and event discovery`
7. `feat: notifications and announcements`
8. `test: automated backend verification`
9. `docs: cloud deployment and submission guide`

Never commit `.env`, passwords, Supabase service-role keys, or other secrets.

## 24. Project report outline

1. Abstract
2. Introduction
3. Problem statement
4. Objectives
5. Existing system and limitations
6. Proposed cloud architecture
7. Technology stack
8. Functional requirements
9. Non-functional requirements
10. Database design
11. Authentication/RBAC
12. REST API design
13. Real-time WebSocket design
14. Capacity concurrency control
15. Waitlist and notification modules
16. Analytics
17. Security
18. Testing and results
19. Cloud deployment
20. Scalability and failure handling
21. Screenshots
22. Conclusion
23. Future enhancements

## 25. Submission checklist

- [ ] `docker compose up -d --build` succeeds on a machine with Docker Desktop
- [ ] Backend `/health` is healthy
- [ ] Sample seed runs
- [ ] Login works
- [ ] Organizer can create event
- [ ] Attendee can RSVP
- [ ] Organizer sees live WebSocket updates
- [ ] Waitlist/capacity demonstration completed
- [ ] Announcement/notification demonstration completed
- [ ] `pytest -q` passes
- [ ] Supabase cloud database verified
- [ ] Screenshots captured
- [ ] README reviewed
- [ ] No secrets committed
- [ ] Final ZIP excludes virtual environments, node_modules, caches and `.git`

## 26. Important production note

This is an educational, portfolio-ready architecture. Before production use, add database migrations (Alembic), structured logging, centralized secret management, rate limiting, CSRF strategy appropriate to the chosen auth transport, stronger audit logging, background job queues, automated integration/load tests, managed WebSocket scaling, and a formal CI/CD pipeline.
