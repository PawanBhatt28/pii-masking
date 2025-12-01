# PII Shield - Enterprise Data Privacy Platform

> Protecting customer privacy in the AI era with intelligent PII masking, secure token vaults, and comprehensive audit trails.

---

## 🎯 Project Overview

**PII Shield** is an API-based privacy layer that automatically detects and masks Personally Identifiable Information (PII) before sending data to external LLMs (OpenAI, Anthropic, etc.), while maintaining the ability to restore original data for authorized users.

### Key Features

- 🎯 **AI-Powered Detection**: 95%+ accuracy across 8 PII types using Presidio + spaCy
- 🔒 **Secure Token Vault**: AES-256 encrypted storage in Redis
- 🔄 **Bidirectional Masking**: Mask for LLMs, unmask for authorized users
- 📊 **Risk Scoring**: Quantify PII exposure risk (0-10 scale)
- 🔍 **Audit Logging**: Immutable compliance trail in MySQL
- ⚡ **Fast**: <300ms p95 latency
- 🔌 **Plug-and-Play**: 5-line integration with existing systems

---

## 📚 Documentation

This repository contains comprehensive documentation for building an enterprise-grade PII masking platform:

### Strategic Documents

1. **[Market Analysis](docs/market_analysis.md)**
   - Market size and opportunity ($25.85B by 2029)
   - Regulatory landscape (GDPR, HIPAA, CCPA, PCI-DSS)
   - Competitive analysis
   - Use cases and business value

2. **[Business Case](docs/business_case.md)**
   - Problem statement and market validation
   - Revenue models ($120K-$480K ARR potential)
   - ROI analysis ($200K-$400K annual value)
   - Go-to-market strategy

3. **[Technical Architecture](docs/architecture_design.md)**
   - System architecture diagrams
   - Component specifications
   - Data flow and security layers
   - Technology stack (FastAPI, Redis, MySQL)

4. **[MVP Specification](docs/mvp_specification.md)**
   - Core features and API endpoints
   - Database schema (MySQL)
   - PII detection specifications
   - Demo scenarios and success metrics

5. **[Implementation Plan](docs/implementation_plan.md)**
   - 3-week development roadmap
   - Daily tasks and deliverables
   - Testing strategy
   - Risk mitigation

6. **[Pitch Deck Outline](docs/pitch_deck_outline.md)**
   - 12-slide presentation structure
   - Talking points for executives
   - Demo strategy

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Your CRM Platform                  │
│  (Voice Bots, Chat Bots, Customer Service)          │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│              PII Shield API Gateway                  │
│  POST /api/v1/mask    | POST /api/v1/unmask         │
│  POST /api/v1/detect  | GET  /api/v1/audit          │
└────────────────────┬────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
   ┌─────────┐  ┌─────────┐  ┌─────────┐
   │Detection│  │ Token   │  │ Audit   │
   │ Engine  │  │ Vault   │  │ Service │
   │(Presidio│  │ (Redis) │  │ (MySQL) │
   │ +spaCy) │  │         │  │         │
   └─────────┘  └─────────┘  └─────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Docker & Docker Compose
- 4GB RAM minimum

### Installation

```bash
# Clone repository
git clone <repository-url>
cd personal-identity-masking

# Start services
docker-compose up -d

# Verify health
curl http://localhost:8000/api/v1/health
```

### Basic Usage

```python
import requests

# Mask PII
response = requests.post("http://localhost:8000/api/v1/mask", json={
    "text": "My name is John Doe, email john@example.com",
    "session_id": "session_123"
})

masked_text = response.json()["masked_text"]
# Output: "My name is [PERSON_a1b2], email [EMAIL_c3d4]"

# Send to LLM safely
openai_response = openai.chat(masked_text)

# Unmask for authorized user
response = requests.post("http://localhost:8000/api/v1/unmask", json={
    "text": masked_text,
    "session_id": "session_123",
    "context": {
        "user_id": "agent_001",
        "user_role": "customer_service"
    }
})

original_text = response.json()["unmasked_text"]
# Output: "My name is John Doe, email john@example.com"
```

---

## 🎯 Supported PII Types

| Type | Examples | Detection Method |
|------|----------|------------------|
| **PERSON** | John Doe, Jane Smith | spaCy NER |
| **EMAIL** | john@example.com | Regex |
| **PHONE** | +1-555-0123, (555) 123-4567 | Regex + phonenumbers |
| **SSN** | 123-45-6789 | Regex |
| **CREDIT_CARD** | 4532-1234-5678-9010 | Regex + Luhn |
| **ADDRESS** | 123 Main St, New York | spaCy NER |
| **DATE_OF_BIRTH** | 01/15/1990 | Regex |
| **IP_ADDRESS** | 192.168.1.1 | Regex |

---

## 📊 Use Cases

### 1. Voice Bot Transcription
Mask customer PII in voice transcripts before sending to LLMs for analysis.

### 2. AI Training Data
Generate masked datasets from real conversations for safe AI model training.

### 3. Third-Party Integrations
Share CRM data with analytics/marketing tools without exposing PII.

### 4. Customer Service
Enable AI-powered agent assistance without data leakage to external LLMs.

---

## 🔒 Security & Compliance

- **Encryption**: AES-256-GCM for data at rest, TLS 1.3 for data in transit
- **Access Control**: Role-based policies for unmasking
- **Audit Trail**: Immutable logs of all PII operations
- **Compliance**: GDPR, HIPAA, CCPA, PCI-DSS ready

---

## 📈 Performance

- **Latency**: <300ms p95 for masking operations
- **Throughput**: 50+ requests/second (MVP), 500+ (production)
- **Accuracy**: 95%+ PII detection accuracy
- **Availability**: 99.5%+ uptime target

---

## 🗺️ Roadmap

### MVP (Weeks 1-3) ✅
- Core masking/unmasking APIs
- 8 PII types supported
- Redis vault + MySQL audit
- Basic compliance dashboard

### Production (Months 1-3)
- SOC2 compliance preparation
- Advanced monitoring (Prometheus + Grafana)
- Multi-region deployment
- Customer onboarding automation

### Enterprise (Months 4-12)
- Synthetic data generation
- Custom NER model training
- Multi-language support
- White-label option

---

## 💰 Business Model

**Premium Tier**: $50-$150/month upsell for PII Shield

**Target Markets**:
- Healthcare CRMs (HIPAA compliance)
- Financial services (PCI-DSS)
- Legal tech (attorney-client privilege)
- EU customers (GDPR)

**Projected Revenue**: $120K-$480K ARR in Year 1

---

## 🤝 Contributing

This is a hackathon project. Contributions welcome after MVP completion.

---

## 📄 License

[To be determined]

---

## 📞 Contact

For questions or demo requests, contact: [Your Name/Email]

---

## 🙏 Acknowledgments

Built with:
- [Microsoft Presidio](https://github.com/microsoft/presidio) - PII detection
- [spaCy](https://spacy.io/) - NER models
- [FastAPI](https://fastapi.tiangolo.com/) - API framework
- [Redis](https://redis.io/) - Token vault
- [MySQL](https://www.mysql.com/) - Audit database

---

**PII Shield**: Building the trust layer for responsible AI innovation. 🚀
