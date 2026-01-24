# Clusterer.py Documentation

## Overview

The `Clusterer` class is responsible for geographically grouping teams into clusters while ensuring each cluster has the correct distribution of meal classes (appetizer, main course, dessert). It uses a two-phase approach: initial clustering followed by rebalancing to meet meal distribution requirements.

## Purpose

In a running dinner event, teams need to be grouped into geographic clusters where:
- Each cluster contains teams hosting different courses (appetizer, main, dessert)
- Teams within a cluster are geographically close to minimize travel distance
- Each cluster must have the exact meal class distribution specified by the cluster template

## Class Structure

### Constructor: `__init__(data_provider: DataProvider)`

Initializes the Clusterer with data from the DataProvider.

**Attributes:**
- `self.routes`: List of `DinnerRoute` objects containing team information
- `self.dist_matrix`: 2D numpy array with precomputed pairwise distances between all teams
- `self.cluster_sizes`: List of integers indicating the number and size of clusters
- `self.cluster_templates`: Dictionary mapping cluster labels to required meal class distributions

**Example cluster_templates:**
```python
{
    0: ['APPETIZER', 'APPETIZER', 'APPETIZER', 'MAIN', 'MAIN', 'MAIN', 'DESSERT', 'DESSERT', 'DESSERT'],
    1: ['APPETIZER', 'APPETIZER', 'APPETIZER', 'MAIN', 'MAIN', 'MAIN', 'DESSERT', 'DESSERT', 'DESSERT'],
    # ... more clusters
}
```

## Core Workflow

### Main Method: `predict()`

This is the primary entry point that performs the complete clustering process.

**Steps:**

1. **Initial Clustering** (via `__predict_draft()`)
2. **Remove Excess Meal Classes**
3. **Fill Missing Meal Classes**

**Returns:** 
- `self.routes`: Updated list of routes with assigned cluster numbers
- `final_cluster_labels`: List of cluster labels for each route

---

## Phase 1: Initial Clustering

### Method: `__predict_draft(n_clusters=None)`

Performs initial geographic clustering using scikit-learn's AgglomerativeClustering.

**Algorithm Details:**
- **Metric:** `precomputed` - Uses the distance matrix directly
- **Linkage:** `complete` - Uses maximum distance between any two points in different clusters
- **n_clusters:** Derived from `len(self.cluster_sizes)` if not specified

**Process:**
1. Creates AgglomerativeClustering model with specified parameters
2. Fits the model on the distance matrix
3. Assigns predicted cluster labels to each route's `clusterNumber` attribute
4. Returns updated routes and labels

**Important:** This initial clustering is **purely geographic** and doesn't consider meal class distribution. The clusters likely have incorrect meal class ratios at this point.

---

## Phase 2: Rebalancing Meal Classes

After initial clustering, the algorithm ensures each cluster has the exact meal class distribution specified in `cluster_templates`.

### Step 2A: Remove Excess Meal Classes

For each cluster, if there are too many teams of a particular meal class:

**Process:**
1. Count current meal classes in the cluster
2. Compare with required counts from `cluster_templates`
3. Identify excess teams for each meal class
4. Remove excess teams using `__remove_excess_meal_classes()`
5. Mark removed teams with `clusterNumber = -1`
6. Add removed team indices to `available_indices` set

### Method: `__remove_excess_meal_classes(routes_of_cluster, meal_class, excess)`

Determines which teams to remove when there's an excess of a meal class.

**Strategy:** Remove teams that are **farthest from the cluster center**.

**Algorithm:**
1. Get all indices of teams in the cluster with the specified meal class
2. For each candidate team:
   - Calculate mean distance to all other teams in the cluster
   - Store as `(mean_distance, original_index)` tuple
3. Sort by mean distance (descending - highest distance first)
4. Select the first `excess` teams for removal
5. Return their indices

**Rationale:** Teams farthest from other cluster members are likely better suited for other clusters or can be reassigned with less impact on intra-cluster distance.

**Example:**
```python
# Cluster has 5 APPETIZER teams but needs only 3
# Calculate mean distances: [(15.2, idx_42), (12.8, idx_17), (10.3, idx_8), (9.1, idx_25), (8.5, idx_33)]
# Remove 2 with highest distances: idx_42 and idx_17
```

---

### Step 2B: Fill Missing Meal Classes

For each cluster, if there are too few teams of a particular meal class:

**Process:**
1. Count current meal classes in the cluster
2. Compare with required counts from `cluster_templates`
3. Identify deficits for each meal class
4. Fill deficits by selecting from `available_indices`

**Selection Strategy:** Choose available teams of the needed meal class that are **closest to the cluster**.

**Algorithm:**
1. Filter `available_indices` to only teams with the needed meal class
2. For each deficit position:
   - Calculate mean distance from each candidate to current cluster members
   - Select candidate with minimum mean distance
   - Assign candidate's `clusterNumber` to this cluster
   - Remove candidate from `available_indices`
   - Add candidate to cluster's index list for next iteration

**Example:**
```python
# Cluster needs 2 more DESSERT teams
# Available DESSERT teams: [idx_42, idx_17, idx_55]
# Mean distances to cluster: [8.3, 12.1, 6.7]
# First pick: idx_55 (distance 6.7)
# Second pick: idx_42 (distance 8.3)
```

**Error Handling:** If there aren't enough available teams of a meal class to fill the deficit, raises `ValueError`.

---

## Utility Methods

### `print_max_distances_per_cluster()`

Diagnostic method that calculates and prints the maximum pairwise distance within each cluster.

**Purpose:** Helps evaluate cluster quality - smaller maximum distances indicate tighter, more geographically compact clusters.

**Process:**
1. For each cluster:
   - Extract indices of all teams in the cluster
   - Create submatrix of distances between cluster members
   - Find maximum distance in upper triangle (avoiding diagonal)
   - Print and return results

**Output Example:**
```
Cluster 0: 9 Elemente, maximale Distanz: 25.43
Cluster 1: 9 Elemente, maximale Distanz: 18.92
Cluster 2: 9 Elemente, maximale Distanz: 31.27
```

### `__print_current_cluster_status(available_indices, cluster_labels_sorted)`

Internal debugging method that logs current state of clustering.

**Prints:**
- Available indices (teams not assigned to any cluster)
- For each cluster:
  - Team indices in the cluster
  - Current meal class distribution

**Used:** After excess removal and after each cluster's missing meal classes are filled.

---

## Key Data Structures

### DinnerRoute Attributes (relevant to Clusterer)

- `originalIndex`: Index in the original data (used for distance matrix lookups)
- `mealClass`: String indicating which course the team hosts ('APPETIZER', 'MAIN', 'DESSERT')
- `clusterNumber`: Integer cluster label (-1 means unassigned/removed)
- `teamNumber`: Unique team identifier

### Special Cluster Number Values

- **`-1`**: Team has been removed from initial cluster assignment and is available for reassignment
- **`0, 1, 2, ...`**: Valid cluster assignments

---

## Algorithm Complexity

**Time Complexity:**
- Initial clustering: O(n² log n) where n is number of teams (AgglomerativeClustering)
- Excess removal: O(k × m × n) where k is number of clusters, m is avg cluster size
- Filling deficits: O(k × d × a × m) where d is deficit count, a is available teams
- Overall: Dominated by initial clustering for large datasets

**Space Complexity:**
- O(n²) for distance matrix
- O(n) for routes and labels
- Overall: O(n²)

---

## Important Invariants

1. **Original Index Preservation:** The `originalIndex` attribute must never change, as it's used for distance matrix lookups
2. **Meal Class Conservation:** Total count of each meal class across all clusters must match input
3. **Cluster Template Adherence:** After `predict()`, each cluster must have exactly the meal distribution specified in `cluster_templates`
4. **No Orphaned Teams:** All teams must be assigned to a cluster by the end of the process (no teams with `clusterNumber == -1`)

---

## Usage Example

```python
from DataProvider import DataProvider
from DefaultClusterer import DefaultClusterer

# Initialize with data
data_provider = DataProvider(routes, distance_matrix, cluster_sizes, cluster_templates)
clusterer = DefaultClusterer(data_provider)

# Perform clustering
clustered_routes, labels = clusterer.predict()

# Optional: Check cluster quality
max_distances = clusterer.print_max_distances_per_cluster()

# Routes now have clusterNumber assigned
for route in clustered_routes:
    print(f"Team {route.teamNumber} in Cluster {route.clusterNumber}, hosts {route.meal}")
```

---

## Logging

The class uses `Log.info()` extensively to provide visibility into the clustering process:
- Current vs required meal class counts per cluster
- Indices being removed due to excess
- Candidates being considered for filling deficits
- Chosen teams and their distances
- Status after each major operation

**Tip:** Enable info-level logging to debug clustering issues or understand why teams are assigned to specific clusters.

---

## Common Issues & Troubleshooting

### Issue: `ValueError: Not enough {meal_class} to fill cluster`

**Cause:** The cluster templates require more teams of a certain meal class than exist in the input data.

**Solution:** 
- Verify input data has correct meal class distribution
- Check cluster templates match the available teams
- Ensure sum of required meal classes across all cluster templates equals total teams

### Issue: Poor geographic clustering

**Symptom:** Teams far apart are in the same cluster (high max distances)

**Possible Causes:**
- Meal class rebalancing moved geographically distant teams together
- Initial clustering parameters not optimal for the distance distribution
- Cluster templates force unnatural groupings

**Solutions:**
- Adjust `linkage` parameter (try 'average' or 'ward')
- Modify cluster templates to allow more flexibility
- Consider preprocessing distance matrix (normalization)

### Issue: Imbalanced cluster sizes

**Cause:** Cluster templates specify uneven cluster sizes

**Solution:** This is expected behavior - clusters are sized according to `cluster_templates`. Verify templates are correct for your use case.

---

## Performance Considerations

- **Distance Matrix:** Must be precomputed and passed in. This allows caching and reuse across multiple optimization runs.
- **Deep Copies:** Not used in this class - works directly on the routes list. RouteBuilder creates deep copies when needed.
- **Logging Overhead:** Extensive logging can slow down large datasets. Consider adjusting log levels for production.

---

## Integration Points

**Input:** Receives data via `DataProvider` which wraps:
- Routes list from input JSON
- Precomputed distance matrix
- Cluster size requirements
- Cluster meal class templates

**Output:** Returns routes with `clusterNumber` assigned, which are then passed to `RouteBuilder` for within-cluster route optimization.

**Caller:** Typically called by `RouteOptimizer.optimize()` as the first major step in the optimization pipeline.

---

## Future Enhancements (Potential)

- **Configurable linkage strategy:** Allow different linkage methods based on data characteristics
- **Multi-objective optimization:** Balance both geographic distance AND meal class distribution in initial clustering
- **Iterative refinement:** After route building, reassess cluster boundaries to reduce total distance
- **Soft constraints:** Allow minor violations of cluster templates if they significantly improve geographic clustering
