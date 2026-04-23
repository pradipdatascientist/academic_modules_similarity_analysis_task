import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.manifold import TSNE
import numpy as np
import argparse
import os

def create_static_vis(input_path, map_output, heatmap_output):
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    # Load results
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    modules = data['modules']
    sim_matrix = np.array(data['similarity_matrix'])
    codes = [m['code'] for m in modules]
    
    # 1. T-SNE Map
    distance_matrix = 1 - sim_matrix
    np.fill_diagonal(distance_matrix, 0)
    
    tsne = TSNE(n_components=2, perplexity=min(30, len(modules)-1), random_state=42, metric='precomputed', init='random')
    vis_coords = tsne.fit_transform(distance_matrix)
    
    df_vis = pd.DataFrame({
        'x': vis_coords[:, 0],
        'y': vis_coords[:, 1],
        'code': codes,
        'level': [f"Level {m['level']}" for m in modules]
    })
    
    plt.figure(figsize=(14, 10))
    sns.set_style("whitegrid")
    scatter = sns.scatterplot(data=df_vis, x='x', y='y', hue='level', style='level', s=120, palette='viridis')
    
    for i, txt in enumerate(df_vis['code']):
        plt.annotate(txt, (df_vis['x'][i], df_vis['y'][i]), xytext=(3, 3), textcoords='offset points', fontsize=8, alpha=0.8)
    
    plt.title('Semantic Module Map (T-SNE)', fontsize=16, fontweight='bold')
    plt.xlabel('T-SNE Dimension 1', fontsize=12)
    plt.ylabel('T-SNE Dimension 2', fontsize=12)
    plt.legend(title='SCQF Level', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(map_output, dpi=300, bbox_inches='tight')
    print(f"Static map saved at {map_output}")

    # 2. Clustered Heatmap
    plt.figure(figsize=(12, 10))
    df_sim = pd.DataFrame(sim_matrix, index=codes, columns=codes)
    
    # Using clustermap for automatic hierarchical clustering
    g = sns.clustermap(df_sim, cmap='viridis', figsize=(15, 15), 
                       xticklabels=True, yticklabels=True,
                       cbar_kws={'label': 'Cosine Similarity'})
    plt.setp(g.ax_heatmap.get_xticklabels(), rotation=90, fontsize=8)
    plt.setp(g.ax_heatmap.get_yticklabels(), rotation=0, fontsize=8)
    plt.title('Clustered Module Similarity Heatmap', fontsize=16, fontweight='bold', pad=100)
    plt.savefig(heatmap_output, dpi=300, bbox_inches='tight')
    print(f"Clustered heatmap saved at {heatmap_output}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create static visualizations for module similarity.')
    parser.add_argument('--input', type=str, default='similarity_results.json', help='Input JSON file path')
    parser.add_argument('--map_output', type=str, default='module_map.png', help='Output PNG file path for map')
    parser.add_argument('--heatmap_output', type=str, default='similarity_heatmap.png', help='Output PNG file path for heatmap')
    args = parser.parse_args()

    create_static_vis(args.input, args.map_output, args.heatmap_output)
