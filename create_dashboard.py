import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.manifold import TSNE
import numpy as np
import argparse
import os

def create_dashboard(input_path, output_path):
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    # Load results
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    modules = data['modules']
    sim_matrix = np.array(data['similarity_matrix'])
    pair_sims = data['pair_similarities']
    
    # 1. T-SNE Visualization (2D Map of Modules)
    distance_matrix = 1 - sim_matrix
    np.fill_diagonal(distance_matrix, 0)
    
    tsne = TSNE(n_components=2, perplexity=min(30, len(modules)-1), random_state=42, metric='precomputed', init='random')
    vis_coords = tsne.fit_transform(distance_matrix)
    
    df_vis = pd.DataFrame({
        'x': vis_coords[:, 0],
        'y': vis_coords[:, 1],
        'code': [m['code'] for m in modules],
        'title': [m['title'] for m in modules],
        'level': [f"Level {m['level']}" for m in modules]
    })
    
    fig_map = px.scatter(df_vis, x='x', y='y', text='code', color='level',
                         hover_data=['title'], title='Semantic Map of Modules (T-SNE)')
    fig_map.update_traces(textposition='top center')
    
    # 2. Similarity Heatmap
    fig_heatmap = go.Figure(data=go.Heatmap(
        z=sim_matrix,
        x=[m['code'] for m in modules],
        y=[m['code'] for m in modules],
        hoverongaps=False,
        colorscale='Viridis'
    ))
    fig_heatmap.update_layout(title='Module Similarity Heatmap', xaxis_title='Module Code', yaxis_title='Module Code')
    
    # Save individual plots as HTML files
    map_plot_path = os.path.join(os.path.dirname(output_path), "module_map_plot.html")
    heatmap_plot_path = os.path.join(os.path.dirname(output_path), "similarity_heatmap_plot.html")

    fig_map.write_html(map_plot_path, include_plotlyjs='cdn', full_html=True)
    fig_heatmap.write_html(heatmap_plot_path, include_plotlyjs='cdn', full_html=True)
    
    # 3. Create a standalone HTML Dashboard with iframes
    dashboard_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset=\"utf-8\" />
        <title>Module Similarity Dashboard</title>
        <style>
            body {{ font-family: sans-serif; margin: 20px; background-color: #f4f4f9; }}
            .container {{ max-width: 1200px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            h1, h2 {{ color: #333; }}
            .chart-container {{ margin-bottom: 40px; border: 1px solid #eee; border-radius: 4px; padding: 10px; }}
            iframe {{ width: 100%; height: 600px; border: none; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #f8f9fa; }}
            tr:hover {{ background-color: #f1f1f1; }}
            .high-sim {{ color: #d9534f; font-weight: bold; }}
            .med-sim {{ color: #f0ad4e; font-weight: bold; }}
            .low-sim {{ color: #5bc0de; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class=\"container\">
            <h1>Academic Module Similarity Analysis</h1>
            <p>This dashboard visualises the semantic similarities between modules in the degree programme based on their aims, learning outcomes, and indicative content.</p>
            
            <h2>1. Semantic Module Map</h2>
            <p>Modules closer together share more similar themes and learning outcomes. Use the tools to zoom and hover for details.</p>
            <div class=\"chart-container\">
                <iframe src=\"{os.path.basename(map_plot_path)}\"></iframe>
            </div>
            
            <h2>2. Top Overlapping Modules</h2>
            <p>The following pairs show the highest semantic similarity, potentially indicating significant content overlap or curriculum progression.</p>
            <table>
                <thead>
                    <tr>
                        <th>Module A</th>
                        <th>Module B</th>
                        <th>Similarity Score</th>
                        <th>Interpretation</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    # Add top overlaps to table
    df_pairs = pd.DataFrame(pair_sims)
    top_pairs = df_pairs.sort_values(by='similarity', ascending=False).head(20)
    for _, row in top_pairs.iterrows():
        sim = row['similarity']
        if sim > 0.85:
            sim_class = "high-sim"
            action = "Possible overlap / duplication risk"
        elif sim > 0.70:
            sim_class = "med-sim"
            action = "Likely topic continuity or progression"
        else:
            sim_class = "low-sim"
            action = "Related but distinct"
            
        dashboard_html += f"""
                    <tr>
                        <td>{row['source']} - {row['source_title']}</td>
                        <td>{row['target']} - {row['target_title']}</td>
                        <td class=\"{sim_class}\">{sim:.2f}</td>
                        <td>{action}</td>
                    </tr>
        """
        
    dashboard_html += f"""
                </tbody>
            </table>
            
            <h2>3. Similarity Heatmap</h2>
            <div class=\"chart-container\">
                <iframe src=\"{os.path.basename(heatmap_plot_path)}\"></iframe>
            </div>
            
            <p><i>Note: High similarity is not automatically a problem; it may reflect deliberate progression between levels.</i></p>
        </div>
    </body>
    </html>
    """
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(dashboard_html)
    
    print(f"Dashboard created at {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create an interactive dashboard for module similarity.')
    parser.add_argument('--input', type=str, default='similarity_results.json', help='Input JSON file path')
    parser.add_argument('--output', type=str, default='dashboard.html', help='Output HTML file path')
    args = parser.parse_args()

    create_dashboard(args.input, args.output)
