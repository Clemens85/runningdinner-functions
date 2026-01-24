# Running Dinner Route Optimization

This is a Python-based AWS Lambda function that optimizes dinner routes for a "running dinner" event, where teams visit each other's homes for different courses. The system clusters teams geographically while respecting meal assignments (appetizer/main/dessert) and minimizes total travel distance.

## Architecture & Data Flow

**Entry Points:**
- **Production (AWS):** [LambdaHandler.py](LambdaHandler.py) - Triggered by S3 events, uses `S3DataLoader` + `AwsResponseHandler`
- **Local Development:** [main.py](main.py) - Uses `LocalFileDataLoader` + `LocalFileResponseHandler`

**Core Pipeline ([RouteOptimizer.py](RouteOptimizer.py)):**
1. Load request JSON with teams, distance matrix, cluster requirements
2. **Clustering** ([Clusterer.py](DefaultClusterer.py)): Initial AgglomerativeClustering, then rebalance meal classes per cluster
3. **Route Building** ([RouteBuilder.py](RouteBuilder.py)): For each cluster, brute-force search matrix templates to find optimal visitor assignments

**Adapter Pattern:** The system uses abstract base classes for environment-agnostic execution:
- `DataLoader` (abstract) → `S3DataLoader` | `LocalFileDataLoader`
- `ResponseHandler` (abstract) → `AwsResponseHandler` (S3 + SNS) | `LocalFileResponseHandler` | `InMemoryResponseHandler` (tests)

**Key Data Structures:**
- `DinnerRoute` (Pydantic models in [DinnerRouteList.py](DinnerRouteList.py)): Represents a team with `meal`, `teamNumber`, `clusterNumber`, `teamsOnRoute` (visitors)
- `DataProvider`: Wraps input data, adds `originalIndex` to routes

## Critical Patterns

### Meal Class Balancing in Clustering
After initial clustering, [Clusterer.predict()](DefaultClusterer.py#L101) performs two-phase rebalancing:
1. **Remove excess:** Teams with wrong meal class are removed based on highest mean distance to cluster
2. **Fill deficits:** Missing meal classes filled by selecting nearest available team from `available_indices`

The cluster size and meal distribution is defined by `cluster_templates` from input data.

### Matrix Template Matching
[MatrixTemplates.py](MatrixTemplates.py) contains hardcoded route patterns (e.g., `matrix9_1`, `matrix9_2` for 9 teams). Each matrix defines which team hosts whom for each course. `RouteBuilder` tries all templates for cluster size and picks the one with minimum total distance.

**Example matrix structure:**
```python
matrix9_1[0]  # Appetizer hosts: [[1, 4, 7], [2, 5, 8], ...] means team 1 hosts teams 4 & 7
matrix9_1[1]  # Main course hosts
matrix9_1[2]  # Dessert hosts
```

### Distance Calculation
`calculate_distance_sum()` in [RouteBuilder.py](RouteBuilder.py#L8): For each route, sum distances from host to all `teamsOnRoute` using pre-computed distance matrix.

## Testing & Development

**Run tests:** Must be executed from package root (configured in [pytest.ini](pytest.ini)):
```bash
cd packages/optimization
pytest
```

**Test data:** Sample team configurations in [test-data/](test-data/) (15_teams.json, 27_teams.json, etc.)

**Local execution:**
- Edit `WORKSPACE_BASE_DIR` in [main.py](main.py) to point to test data directory
- Update placeholders: `__ADMIN_ID__`, `__OPTIMIZATION_ID__`
- Run: `python main.py`

**Debugging:** Use `Visualizer.plot_geocodes()` to visualize team locations and clusters (requires matplotlib)

## AWS Integration

- S3 trigger → Lambda reads request JSON from S3
- Response written to S3 (mapped via [ResponseKeyMapper](aws_adapter/ResponseKeyMapper.py))
- SNS notification sent to `SNS_TOPIC_ARN` with optimization status
- Error handling: Catches exceptions, sends error JSON + event to response handlers
- Tracing: Uses AWS Lambda Powertools (`@tracer`, `@metrics`, logging via `Log.inject_lambda_context`)

## Important Constraints

- All routes must maintain original `originalIndex` (used for distance matrix lookups)
- Deep copies used in `RouteBuilder` to avoid mutating original data
- `clusterNumber = -1` marks teams removed from clusters (available for reassignment)
- Distance matrix is precomputed and passed in request (not calculated here)
