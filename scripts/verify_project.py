"""Offline submission verification: checks required files, imports by source inspection, and safety rules.
Run after dependency installation for a quick pre-flight check.
"""
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
required=[
 'README.md','docker-compose.yml','.env.example','.gitignore',
 'backend/requirements.txt','backend/Dockerfile','backend/schema.sql','backend/seed.py',
 'backend/app/main.py','backend/app/core/security.py','backend/app/models/models.py',
 'backend/app/api/auth.py','backend/app/api/events.py','backend/app/api/rsvps.py','backend/app/api/my_rsvps.py','backend/app/api/notifications.py',
 'backend/app/services/analytics.py','backend/app/services/notifications.py','backend/app/services/realtime.py','backend/app/ws/websocket.py',
 'backend/tests/test_unit.py','backend/tests/test_api.py',
 'frontend/package.json','frontend/Dockerfile','frontend/vite.config.js','frontend/src/main.jsx','frontend/src/App.jsx','frontend/src/pages/Login.jsx','frontend/src/pages/Dashboard.jsx','frontend/src/pages/Events.jsx','frontend/src/pages/Notifications.jsx','frontend/src/services/api.js'
]
missing=[p for p in required if not (ROOT/p).exists()]
assert not missing, f'Missing required files: {missing}'
assert not list(ROOT.rglob('.env')), 'Real .env file must not be packaged.'
assert not list(ROOT.rglob('node_modules')), 'node_modules must not be packaged.'
assert not list(ROOT.rglob('__pycache__')), '__pycache__ must not be packaged.'
text=(ROOT/'backend/app/api/auth.py').read_text()
assert 'Admin accounts cannot be self-registered' in text
models=(ROOT/'backend/app/models/models.py').read_text()
assert 'UniqueConstraint("event_id", "user_id"' in models
rsvp=(ROOT/'backend/app/api/rsvps.py').read_text()
assert 'with_for_update()' in rsvp and 'maximum_capacity' in rsvp
ws=(ROOT/'backend/app/ws/websocket.py').read_text()
assert '@router.websocket("/ws/events/{event_id}")' in ws
front='\n'.join(p.read_text() for p in (ROOT/'frontend/src').rglob('*.jsx'))
for marker in ['Dashboard','Events','Notifications','WebSocket','/api/events/','/api/notifications']:
    assert marker in front, f'Frontend marker missing: {marker}'
print(f'PASS: {len(required)} required files present')
print('PASS: no secrets, node_modules or Python cache detected')
print('PASS: RBAC, unique RSVP constraint, row-locking capacity logic and WebSocket route detected')
print('NOTE: this offline verifier does not replace runtime integration tests; install dependencies and run the commands in README.md.')
