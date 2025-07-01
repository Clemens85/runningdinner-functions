import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
sns.set(style="whitegrid")

class Visualizer:
    def __init__(self, routes, dist_matrix):
        self.routes = routes.copy()  # Ensure we don't modify the original DataFrame
        self.dist_matrix = dist_matrix
        self.cluster_ids = self.routes['clusterNumber'].unique()
        palette = sns.color_palette("deep", len(self.cluster_ids))
        self.cluster_color_map = dict(zip(self.cluster_ids, palette))

    def plot_geocodes(self):
        plt.figure(figsize=(12, 8))
        sns.scatterplot(data=self.routes, x='lng', y='lat', hue='clusterNumber', style='mealClass',
                        s=80, alpha=0.8, edgecolor='black', linewidth=0.7,
                        palette=self.cluster_color_map)
        # for cluster_id in self.cluster_ids:
        #     cluster_data = self.routes[self.routes['clusterNumber'] == cluster_id]
        #     plt.scatter(cluster_data['lng'], cluster_data['lat'],
        #                 label=f"Cluster {cluster_id}",
        #                 color=self.cluster_color_map[cluster_id],
        #                 s=80, alpha=0.8, edgecolor='black', linewidth=0.7)
        # plt.title("Geopunkte nach Cluster")
        # plt.xlabel("Längengrad")
        # plt.ylabel("Breitengrad")
        # plt.legend()
        # plt.grid(True)
        plt.show()

    def plot_distance_matrix(self):
        mask = np.tril(np.ones_like(self.dist_matrix, dtype=bool))
        # --- 2. Heatmap der Distanzmatrix ---
        plt.figure(figsize=(14, 8))
        sns.heatmap(self.dist_matrix,
                    mask=mask,
                    annot=False, fmt=".1f", cmap="YlGnBu",
                    xticklabels=[f'#{i}' for i in range(len(self.routes))],
                    yticklabels=[f'#{i}' for i in range(len(self.routes))])
        plt.title("Distanzmatrix zwischen Objekten")
        plt.xlabel("Zielobjekt")
        plt.ylabel("Quellobjekt")
        plt.show()

    def plot_distance_threshold(self, bins=50):
        # Assuming dist_matrix is your numpy array
        # Get the upper triangle values, excluding the diagonal
        dists = self.dist_matrix[np.triu_indices_from(self.dist_matrix, k=1)]
        dists = dists[dists > 0]  # Exclude zeros if present
        
        plt.figure(figsize=(12, 8))
        plt.hist(dists, bins=bins)
        plt.title("Histogram of Pairwise Distances")
        plt.xlabel("Distance")
        plt.ylabel("Frequency")
        plt.show()
        # Print some percentiles for guidance
        for p in [50, 75, 90, 95, 99]:
            print(f"{p}th percentile: {np.percentile(dists, p)}")

    def plot_max_distances_per_cluster(self, distances_per_cluster):
        plt.figure(figsize=(12, 6))
        cluster_sizes = pd.Series(distances_per_cluster)
        cluster_sizes = cluster_sizes.sort_index()  # Sort by cluster ID for better visualization
        plt.bar(cluster_sizes.index, cluster_sizes.values, color=sns.color_palette("viridis", len(cluster_sizes)))
        plt.title("Maximale Distanz pro Cluster")
        plt.xlabel("Cluster ID")
        plt.ylabel("Maximale Distanz")
        plt.xticks(rotation=45)
        plt.grid(axis='y')
        plt.show()
