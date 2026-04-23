import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import argparse
import os

def analyze_similarity(input_path, output_path):
    # Load modules
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    with open(input_path, 'r', encoding='utf-8') as f:
        modules = json.load(f)
    
    # Prepare text for embedding
    # We weight learning outcomes more heavily by repeating them in the combined string
    texts = []
    for m in modules:
        title = m.get('title', '')
        aim = m.get('aim', '')
        lo = ' '.join(m.get('learning_outcomes', []))
        content = m.get('indicative_content', '')
        # Weighting LOs by repeating them
        combined_text = f"{title}. {aim}. {lo} {lo}. {content}"
        texts.append(combined_text)
    
    # Load model
    print("Loading embedding model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Generate embeddings
    print("Generating embeddings...")
    embeddings = model.encode(texts)
    
    # Calculate cosine similarity matrix
    sim_matrix = cosine_similarity(embeddings)
    
    # Create a list of similarities for visualization
    similarities = []
    for i in range(len(modules)):
        for j in range(i + 1, len(modules)):
            similarities.append({
                'source': modules[i]['code'],
                'target': modules[j]['code'],
                'source_title': modules[i]['title'],
                'target_title': modules[j]['title'],
                'similarity': float(sim_matrix[i][j])
            })
    
    # Save results
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            'modules': modules,
            'similarity_matrix': sim_matrix.tolist(),
            'pair_similarities': similarities
        }, f, indent=2)
    
    # Identify top overlaps
    df = pd.DataFrame(similarities)
    top_overlaps = df.sort_values(by='similarity', ascending=False).head(20)
    print("\nTop 20 Module Overlaps:")
    print(top_overlaps[['source', 'target', 'similarity']])
    print(f"\nResults saved to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Analyze module similarity using semantic embeddings.')
    parser.add_argument('--input', type=str, default='modules.json', help='Input JSON file path')
    parser.add_argument('--output', type=str, default='similarity_results.json', help='Output JSON file path')
    args = parser.parse_args()

    analyze_similarity(args.input, args.output)
