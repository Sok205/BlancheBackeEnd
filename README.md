# Backend for the Hackathon project: Mimir

## Description
A FastAPI-based backend service for managing Mimir app

## Features
- User registration and authentication
- Event creation and management
- Event participation system
- AI-powered event descriptions using Tiny-Viking-1.1b model
- SQLite database integration

## Tech Stack
- Python 3.13
- FastAPI
- SQLAlchemy
- HuggingFace Transformers
- SQLite

## API Endpoints
- `/api/register` - User registration
- `/api/login` - User authentication
- `/api/event/create` - Create new events
- `/api/event/join` - Join existing events
- `/api/event/all` - List all events
- `/api/event/{event_id}` - Get event details
- `/api/event/ai/{event_id}` - Get AI-generated insights

## Setup
1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the server 

```bash
uvicorn main:app --host 0.0.0.0 --port 8000    
```

## Building and Running the docker container with ai model
1. Set up your Hugging Face access token:
```bash
export HF_ACCESS_TOKEN=your_huggingface_token
```

2. Build the Docker image:
```bash
docker compose up --build
```

* This will build the container with the Tiny-Viking-1.1b model and expose it on port 8080. The model files will be cached in the `./cache` directory to speed up subsequent runs.