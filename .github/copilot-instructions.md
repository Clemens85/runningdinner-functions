# RunningDinner Functions - AI Coding Agent Instructions

## Project Architecture

This is a **hybrid TypeScript/Python serverless** project for optimizing dinner party routes using AWS CDK, Lambda, and ML clustering algorithms. The system geocodes addresses, groups participants into clusters, and optimizes travel routes between dinner locations.

### Core Components

- **`packages/geocoding`** - Shared TypeScript library for address geocoding via Google Maps API
- **`packages/geocoding-http`** - Lambda function URL endpoint for batch geocoding requests
- **`packages/geocoding-sqs`** - SQS-triggered Lambda for async geocoding processing
- **`packages/optimization`** - Python ML service for route clustering and optimization using scikit-learn
- **`infrastructure/`** - AWS CDK stacks for deployment (`GeocodingStack`, `RouteOptimizationStack`)

### Key Data Flow

1. HTTP requests → `geocoding-http` Lambda → SQS queue → `geocoding-sqs` Lambda → DynamoDB cache
2. S3 optimization requests → `optimization` Lambda → SNS notifications
3. Teams are clustered by geographic proximity, then optimal dinner routes calculated per cluster

## Development Workflows

### Build & Test Commands

```bash
# Root level - typecheck all packages
pnpm recursive run typecheck

# Individual packages
cd packages/geocoding && pnpm test
cd packages/optimization && python -m pytest tests/
```

### AWS Deployment (requires aws-vault)

```bash
cd infrastructure/

# Bootstrap (first time only)
./bootstrap.sh <stage>  # stage = dev|prod

# Deploy specific stacks
./deploy-geocoding.sh <stage>
./deploy-route-optimization.sh <stage>

# Create Python layer (before route optimization)
cd lib && ./create-route-optimization-layer.sh
```

### Development Environment

- **Python**: Uses Jupyter notebooks in `packages/optimization/playground.ipynb` for ML experimentation
- **AWS**: Configured via `RUNNINGDINNER_FUNCTIONS_STAGE` environment variable
- **Local dev**: `LocalDevUserStack` creates IAM users and permissions and o ther AWS entities for local development purposes and testing

## Critical Patterns

### Lambda Function Structure

- **TypeScript**: Export `handler` with AWS event types (`LambdaFunctionURLHandler`, `SQSHandler`)
- **Python**: Use `@tracer.capture_lambda_handler` and structured logging via `Log.inject_lambda_context`

### Data Models (Python)

- All models use **Pydantic** (`DinnerRoute`, `TeamsOnRoute`, `GeocodingResult`)
- Routes have `originalIndex` for distance matrix lookups, `clusterNumber` for grouping
- Meal classes: `"Vorspeise"`, `"Hauptspeise"`, `"Nachspeise"` (German: appetizer, main, dessert)

### Route Optimization Algorithm

- **Clusterer**: Groups teams by geographic proximity using scikit-learn
- **RouteBuilder**: Solves assignment problem using brute force over matrix templates
- **Matrix Templates**: Pre-defined hosting patterns (e.g., 9-team cluster = 3x3 matrix)

### AWS Infrastructure Patterns

- **Environment-specific**: `Environment.ts` configures resources based on `RUNNINGDINNER_FUNCTIONS_STAGE`
- **Custom CDK constructs**: `NodeJsLambda`, `PythonLambda` for consistent Lambda deployment
- **SQS with DLQ**: All queues have dead letter queues with `maxReceiveCount: 2`

### Shared Package Usage

```typescript
// Import from geocoding package
import { GeocodingApiServiceCached, Util } from "@runningdinner/geocoding";

// DynamoDB key pattern
pk: `GEOCODING#${address.toAddressString()}`;
sk: `RESULT#${uuidv4()}`;
```

## Important Notes

- **esbuild version**: Must be `< 0.22.x` (specified in infrastructure/package.json)
- **Python layer**: Route optimization requires manual layer creation before deployment
- **Testing**: Python tests use real data files in `test-data/` directory
- **Caching**: Geocoding results cached in DynamoDB with TTL for cost optimization
- **Error handling**: All Lambda functions use structured logging and SNS for notifications

## File Naming Conventions

- CDK stacks: `*Stack.ts`
- Lambda handlers: `index.ts` (TypeScript), `LambdaHandler.py` (Python)
- Test files: `test_*.py` (Python), `*.spec.ts` (TypeScript)
- AWS resources named with stage suffix: `route-optimization-${stage}`
