##ZTNA-Demo (Flask + OPA)
# Running Instructions
1. ```pip install flask``` (windows)
2. ```python ztna_demo.py```

A minimal Zero Trust Network Access demo that protects internal apps using:
- JWT authentication (identity)
- device posture headers (trusted device, geo, MFA)
- Open Policy Agent (OPA) for centralized authorization decisions

### Quickstart
1. Start services
   - docker compose up -d --build

2. Run end-to-end demo
   - ./scripts/demo.sh

App runs on http://localhost:5001  
OPA runs on http://localhost:8181

### What the demo shows
- Alice (engineering) can access `/apps/eng` only when posture checks pass
- Alice is denied for `/apps/finance`
- Bob (finance) is allowed for `/apps/finance` only with MFA posture

### Key endpoints
- POST /login
- GET /apps/eng
- GET /apps/finance
- GET /healthz

### Posture headers used by the demo
- X-Device-Trusted: true|false
- X-MFA: true|false
- X-Geo: IN|US|...

### Architecture (high level)
Client -> Flask gateway -> OPA policy decision -> allow/deny -> protected app response
