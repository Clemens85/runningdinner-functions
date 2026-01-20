# RunningDinner Functions - AI Agent Instructions

## Project Overview

Hybrid TypeScript/Python serverless application for optimizing dinner party routes using AWS CDK, Lambda, and ML clustering. Components communicate via S3 events, SQS queues, and SNS notifications.

## Architecture

- **`packages/geocoding`** - Shared TypeScript library for Google Maps geocoding
- **`packages/geocoding-http`** - Lambda function URL for batch geocoding
- **`packages/geocoding-sqs`** - SQS-triggered async geocoding with DynamoDB caching
- **`packages/optimization`** - Python ML service using scikit-learn for route clustering optimization
- **`packages/message-proposal`** - LLM-based message generation using OpenAI
- **`packages/support-bot`** - LangGraph-based chatbot with Pinecone vector DB
- **`infrastructure/`** - AWS CDK stacks (all stacks instantiated in `bin/infrastructure.ts`)

**Critical constraint**: All CDK stacks are always instantiated regardless of which stack you're deploying. This means `RouteOptimizationStack` requires `infrastructure/lib/layers/route_optimization` directory to exist even when deploying other stacks.

### Key Data Flow

1. HTTP requests → `geocoding-http` Lambda → SQS queue → `geocoding-sqs` Lambda → DynamoDB cache
2. S3 optimization requests → `optimization` Lambda → SNS notifications
3. Teams are clustered by geographic proximity, then optimal dinner routes calculated per cluster

## Development Workflows

### Monorepo Structure (pnpm)
```bash
# Root commands affect TypeScript packages only (Python excluded in pnpm-workspace.yaml)
pnpm recursive run typecheck  # Typecheck all TS packages
pnpm lint                     # Lint all TS packages
pnpm build                    # Build all TS packages
```

### Testing
```bash
# TypeScript (vitest)
cd packages/geocoding && pnpm test        # Local tests
cd packages/geocoding && pnpm test:ci     # CI with JUnit reports

# Python (pytest)
cd packages/optimization && python -m pytest tests/
cd packages/message-proposal && PYTHONPATH=. pytest --junitxml=reports/junit.xml --cov=.
```

### Local Development

**Python packages** use adapter pattern for local testing:
- `aws_adapter/` - Production AWS integrations (S3, SSM, SNS)
- `local_adapter/` - Local file-based implementations
- Tests use `.env` files (via `python-dotenv`) - example: `packages/message-proposal/tests/.env`

**Environment detection**: Check `os.environ.get("AWS_LAMBDA_FUNCTION_NAME")` to determine if running in Lambda

**Local servers**:
```bash
# Support bot web UI
cd packages/support-bot && python run_local_server.py  # FastAPI on :8000

# Route optimization file watcher
cd packages/optimization && python main_watcher.py  # Watches test-data/ for *-request.json
```

### AWS Deployment

**Environment variable**: `RUNNINGDINNER_FUNCTIONS_STAGE=dev|prod` determines resource configuration via `infrastructure/lib/Environment.ts`

**Local deployment (requires aws-vault)**:
```bash
cd infrastructure/
./bootstrap.sh dev                    # First-time CDK bootstrap
./deploy-geocoding.sh dev            # Deploy geocoding stack
./deploy-route-optimization.sh dev   # Deploy optimization stack

# Route optimization requires layer build first
cd lib && ./create-route-optimization-layer.sh  # Docker-based scikit-learn build
```

**GitHub Actions**:
- Build workflows: `build-{geocoding,route-optimization,message-proposal}.yml` - Run on path-specific pushes
- Deploy workflows: `deploy-{geocoding,support-bot}.yml` - Manual dispatch with environment selection
- All deployments need placeholder: `mkdir -p infrastructure/lib/layers/route_optimization` (CDK requirement)
- Uses OIDC auth (no AWS credentials in secrets) via `role/github` with PowerUserAccess

## Critical Patterns

### CDK Custom Constructs
- **`NodeJsLambda`** - TypeScript Lambda with esbuild bundling (must use esbuild < 0.22.x)
- **`PythonLambda`** - Python Lambda with asset bundling and exclusion patterns
- **Environment-specific naming**: All resources use `${name}-${ENVIRONMENT.stage}` pattern

### Lambda Handlers
**TypeScript**: Export `handler` with AWS SDK types
```typescript
import { LambdaFunctionURLHandler } from 'aws-lambda';
export const handler: LambdaFunctionURLHandler = async (event) => { ... }
```

**Python**: Use Powertools decorators
```python
from aws_lambda_powertools import Tracer, Logger
tracer = Tracer()
logger = Logger()

@tracer.capture_lambda_handler
@logger.inject_lambda_context(log_event=True)
def lambda_handler(event: dict, context: LambdaContext):
```

### Data Models (Python)
- All use **Pydantic** for validation (`DinnerRoute`, `GeocodingResult`, `TeamsOnRoute`)
- Routes have `originalIndex` (for distance matrix) and `clusterNumber` (for grouping)
- Meal classes: `"Vorspeise"`, `"Hauptspeise"`, `"Nachspeise"` (German)

### Route Optimization Algorithm

- **Clusterer**: Groups teams by geographic proximity using scikit-learn
- **RouteBuilder**: Solves assignment problem using brute force over matrix templates
- **Matrix Templates**: Pre-defined hosting patterns (e.g., 9-team cluster = 3x3 matrix)

### Shared Package Usage

```typescript
// Import from geocoding package
import { GeocodingApiServiceCached, Util } from "@runningdinner/geocoding";

// DynamoDB key pattern
pk: `GEOCODING#${address.toAddressString()}`;
sk: `RESULT#${uuidv4()}`;
```

### Cross-Stack References
`GithubOidcStack` uses `geocodingStack.table` - demonstrates cross-stack dependencies in `bin/infrastructure.ts`

## File Naming Conventions
- CDK stacks: `*Stack.ts`
- Lambda handlers: `index.ts` (TS), `LambdaHandler.py` (Python)
- Tests: `test_*.py` (Python), `*.spec.ts` (TypeScript)
- Deploy scripts: `deploy-*.sh` with stage parameter

## Common Issues
1. **Missing layer directory**: GitHub Actions must create `infrastructure/lib/layers/route_optimization` before CDK synth
2. **esbuild version**: Infrastructure must pin esbuild < 0.22.x
3. **Python excluded from pnpm**: Python packages (`optimization`, `support-bot`) excluded in `pnpm-workspace.yaml`
4. **SSM parameters**: API keys stored in AWS Parameter Store (`/runningdinner/{googlemaps,openai,pinecone}/apikey`)
