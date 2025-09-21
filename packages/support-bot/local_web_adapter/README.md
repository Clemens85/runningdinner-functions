# Running Dinner Support Bot - Local Development

This directory contains a local web server implementation for the Support Bot to allow testing without deploying to AWS Lambda.

## Setup

1. Make sure you have installed the development dependencies:

```bash
pip install -r requirements-dev.txt
```

2. Create a `.env` file in the `support-bot` directory by copying `.env.example` and filling in your API keys:

```bash
cp .env.example .env
# Edit .env with your API keys
```

## Running the Local Server

You can run the local server in two ways:

### Option 1: Using the convenience script

```bash
python run_local_server.py
```

or

```bash
./run_local_server.py
```

### Option 2: Running the module directly

```bash
python -m local_web_adapter.LocalApiHandler
```

## API Endpoints

The server provides these endpoints:

- `POST /api/support` - Main support bot endpoint
- `GET /health` - Health check endpoint

## Example Request

```bash
curl -X POST http://localhost:8000/api/support \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How do I create a Running Dinner event?",
    "thread_id": "example-thread-123"
  }'
```

## Development

The `LocalApiHandler.py` file implements a FastAPI server that mimics the AWS Lambda interface but runs locally. It uses the same `SupportRequestHandler` as the Lambda function to ensure consistent behavior.
