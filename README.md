# LLM Knowledge Extractor

## Setup and Run Instructions

### Prerequisites

- Python 3.10+
- Open AI or Claude Key or Ollama for local models

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp env.example .env
```

### Configuration

Edit `.env` file to set your preferred LLM provider:

- `LLM_CLIENT`: Choose from `openai`, `claude`, `ollama`, or `mock`
- Add API keys for cloud providers (OpenAI, Claude)
- Configure model names and other settings

### Running the Application

#### Local Development (Recommended)

```bash
uvicorn app.main:app --reload
```

#### Docker

```bash
# Copy Docker environment
cp env.docker .env

# Start with Docker Compose
docker-compose up -d
```

### API Endpoints

- `POST /analyze` - Analyze text and extract knowledge
- `GET /search?topic=xyz` - Search stored analyses by topic or keywords

## Design Choices

I structured this application using a **modular, service-oriented architecture** to ensure clean separation of concerns and easy extensibility. The codebase is organized into distinct layers: API routes handle HTTP requests, services contain business logic (LLM analysis, NLP processing), database operations are abstracted through CRUD functions, and configuration is centralized using Pydantic settings. I chose **FastAPI** for its excellent performance, automatic API documentation, and built-in validation, while **SQLite** provides zero-configuration persistence that's perfect for development and small-scale deployments. The **multi-provider LLM support** (OpenAI, Claude, local Ollama) is implemented through a factory pattern in the config layer, allowing easy switching between providers without changing business logic. External prompt files and comprehensive logging ensure the system is both customizable and observable.

## Trade-offs Due to Time Constraints

Due to time limitations, I made several pragmatic trade-offs: **no frontend interface** was built, requiring users to interact via API calls or the auto-generated Swagger docs. I used **SQLite instead of PostgreSQL** for simplicity, though the modular database layer makes migration straightforward. **NLTK was replaced with a simple regex-based keyword extractor** to avoid dependency management issues, sacrificing some NLP sophistication for reliability. The **Docker setup is basic** without production optimizations like multi-stage builds or security hardening. Finally, **error handling is functional but not exhaustive**, with basic HTTP status codes rather than detailed error categorization and recovery strategies. **Bonus** Some bonus features like tests, batch processing and confidence score was not done because of time constraint.
