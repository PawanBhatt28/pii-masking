# MVP Specification: PII Shield Platform

## Executive Summary

**Goal**: Build a production-ready PII masking system with masking, unmasking, and audit capabilities.

**Timeline**: 2-3 weeks hackathon

**Architecture**: API-first lightweight middleware with enterprise features

---

## Core Features (Must-Have)

| Feature | Priority | Effort | Description |
|---------|----------|--------|-------------|
| **PII Detection** | P0 | 3 days | Detect 8 PII types using Presidio + spaCy |
| **Masking API** | P0 | 2 days | Convert PII to tokens, store in Redis vault |
| **Unmasking API** | P0 | 2 days | Restore original PII with access control |
| **Token Vault** | P0 | 2 days | Redis-based secure storage with AES-256 encryption |
| **Audit Logging** | P0 | 2 days | Immutable MySQL logs of all operations |
| **API Authentication** | P0 | 1 day | API key-based authentication |
| **Health Checks** | P0 | 0.5 days | System monitoring endpoints |

**Total**: ~12.5 days

---

## API Endpoints

### 1. POST /api/v1/mask
Detect and mask PII in text.

**Request**:
```json
{
  "text": "My name is John Doe, email john@example.com",
  "session_id": "session_abc123",
  "context": {
    "user_id": "agent_001",
    "purpose": "customer_support"
  }
}
```

**Response**:
```json
{
  "success": true,
  "masked_text": "My name is [PERSON_a1b2], email [EMAIL_c3d4]",
  "entities": [
    {
      "type": "PERSON",
      "token": "[PERSON_a1b2]",
      "confidence": 0.95
    }
  ],
  "risk_score": 6.5
}
```

### 2. POST /api/v1/unmask
Restore original PII from masked text.

**Request**:
```json
{
  "text": "Contact [PERSON_a1b2] at [EMAIL_c3d4]",
  "session_id": "session_abc123",
  "context": {
    "user_id": "agent_001",
    "user_role": "customer_service",
    "reason": "Verify customer identity"
  }
}
```

**Response**:
```json
{
  "success": true,
  "unmasked_text": "Contact John Doe at john@example.com",
  "audit_id": "audit_xyz789"
}
```

### 3. POST /api/v1/detect
Detect PII without masking (analysis only).

### 4. GET /api/v1/audit
Retrieve audit logs with filtering.

### 5. GET /api/v1/health
Health check for monitoring.

---

## Technology Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| **API Framework** | FastAPI (Python) | Fast, async, auto-docs |
| **PII Detection** | Presidio + spaCy | Production-ready NER |
| **Token Vault** | Redis Cluster | In-memory speed, TTL support |
| **Audit Database** | MySQL 8.0 | ACID compliance, familiar |
| **Encryption** | Fernet (AES-256) | Simple, secure |
| **Containerization** | Docker | Easy deployment |

---

## Database Schema (MySQL)

### Audit Events Table
```sql
CREATE TABLE audit_events (
    event_id VARCHAR(50) PRIMARY KEY,
    timestamp DATETIME(6) NOT NULL,
    operation VARCHAR(20) NOT NULL,
    session_id VARCHAR(50),
    user_id VARCHAR(50),
    user_role VARCHAR(50),
    ip_address VARCHAR(45),
    pii_types_accessed JSON,
    purpose VARCHAR(100),
    reason TEXT,
    success BOOLEAN,
    metadata JSON,
    created_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6),
    INDEX idx_session (session_id),
    INDEX idx_user (user_id),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB;
```

---

## PII Types Supported (MVP)

- **PERSON** - Names (NER-based)
- **EMAIL** - Email addresses (regex)
- **PHONE** - Phone numbers (international)
- **SSN** - Social Security Numbers
- **CREDIT_CARD** - Payment cards (with Luhn validation)
- **ADDRESS** - Physical addresses
- **DATE_OF_BIRTH** - Birth dates
- **IP_ADDRESS** - IP addresses

---

## Demo Scenarios

### Demo 1: Basic Masking
Show raw text → masked text → send to OpenAI safely

### Demo 2: Risk Scoring
Low-risk (name only) vs High-risk (SSN + CC)

### Demo 3: Access Control
Agent can unmask email ✓, but not SSN ✗

### Demo 4: Audit Trail
Show complete audit log with filtering

### Demo 5: Integration
5 lines of code to integrate with existing CRM

---

## Success Metrics

- ✅ All 5 APIs functional
- ✅ <300ms p95 latency
- ✅ 95%+ detection accuracy
- ✅ CEO/CTO approval
- ✅ 3+ customer pilot commitments
