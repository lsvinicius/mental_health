# Mental Health Crisis Detection System

A mental health crisis detection system that analyzes conversations between patients and AI to assess risks of self-harm and suicide using Event Sourcing and CQRS patterns.

## 🎯 Purpose

This system provides:
- **Real-time conversation management** between patients and AI assistants
- **Automated risk assessment** using Google's Gemini AI to detect signs of self-harm or suicidal ideation
- **Event-sourced architecture** for complete conversation history and audit trails
- **Asynchronous processing** of risk analysis through an outbox pattern
- **RESTful API** for integration with frontend applications

## 🏗️ Architecture

The system implements **Event Sourcing** and **CQRS (Command Query Responsibility Segregation)** patterns:

### Event Sourcing
- All state changes are stored as immutable events
- Complete audit trail of all conversations
- Ability to reconstruct state at any point in time
- Events: `CONVERSATION_STARTED`, `NEW_MESSAGE`, `CONVERSATION_DELETED`

### CQRS
- **Commands**: Modify state (handled by `ConversationCommandHandler`)
- **Queries**: Read state from projections (handled by `ConversationQueryHandler`)
- **Projections**: Read models built from events for efficient querying

### Outbox Pattern
- Background processor reads unprocessed events
- Projects events into read models
- Triggers risk analysis asynchronously
- Ensures eventual consistency

### Components

```
┌─────────────┐
│  FastAPI    │  ← REST API endpoints
└──────┬──────┘
       │
       ├──────────────────────────────────┐
       │                                  │
┌──────▼───────────────┐          ┌──────▼──────────────┐
│  Command Handler     │          │  Query Handler      │
└──────┬───────────────┘          └──────┬──────────────┘
       │                                  │
       │                                  │ (reads from)
┌──────▼──────────┐              ┌───────▼──────────────┐
│  Event Store    │              │    Projections       │
│  (Outbox)       │              │  - Conversations     │
└──────┬──────────┘              │  - Messages          │
       │                         └───────▲──────────────┘
       │                                 │
       │                                 │ (generates)
┌──────▼──────────────┐                  │
│  Outbox Processor   │──────────────────┘
│  (Background)       │
└──────┬──────────────┘
       │
       │ (triggers)
┌──────▼──────────────┐
│  Risk Analyzer      │  ← Google Gemini AI
└─────────────────────┘
```

## ✨ Features

- ✅ User management
- ✅ Conversation lifecycle management
- ✅ Real-time message handling
- ✅ AI-powered risk assessment using Google Gemini
- ✅ Automatic background processing
- ✅ Complete conversation history
- ✅ Timezone-aware queries
- ✅ Ownership validation (users can only access their own conversations)

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- Docker & Docker Compose
- Poetry (for local development)
- Google API Key (for Gemini AI)

### Setup with Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd mental_health
   ```

2. **Create `.env` file**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` with your configuration:

3. **Start the services**
   ```bash
   docker compose up --build
   ```

4. **Run migrations**
   ```bash
   docker compose exec web alembic upgrade head
   ```

5. **Access the application**
   - API: http://localhost:8000
   - API Docs (Swagger): http://localhost:8000/docs
   - PgAdmin: http://localhost:8888

### Local Development Setup

1. **Install Poetry**
   ```bash
   curl -sSL https://install.python-poetry.org | python3 - --version 1.8.4
   ```

2. **Install dependencies**
   ```bash
   poetry install
   ```

3. **Set up local PostgreSQL**
   ```bash
   docker-compose up db -d
   ```

4. **Create `.env` file for local development**

5. **Run migrations**
   ```bash
   poetry run alembic upgrade head
   ```

6. **Start the application**
   ```bash
   poetry run python -m src.main
   ```

## 🧪 Running Tests

### All tests
```bash
poetry run pytest
```
