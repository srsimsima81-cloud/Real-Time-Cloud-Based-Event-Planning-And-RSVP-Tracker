# API Examples

## Login
```json
POST /api/login
{"email":"organizer@demo.local","password":"Organizer@123"}
```

## Create event
```json
POST /api/events
Authorization: Bearer <JWT>
{"event_name":"Cloud Computing Workshop","description":"Fictional workshop","event_type":"Workshop","event_date":"2030-10-10","start_time":"10:00:00","end_time":"13:00:00","venue":"Skyline Learning Hub","maximum_capacity":100,"registration_deadline":"2030-10-09T18:00:00Z","status":"PUBLISHED"}
```

## RSVP
```json
POST /api/events/1/rsvp
Authorization: Bearer <JWT>
{"status":"GOING"}
```
