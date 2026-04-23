import subprocess
import sys
import os
import argparse

def run_command(command):
    print(f"\n>>> Running: {' '.join(command)}")
    result = subprocess.run(command, capture_output=False, text=True)
    if result.returncode != 0:
        print(f"Error executing command: {' '.join(command)}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Run the full module similarity analysis pipeline.')
    parser.add_argument('pdf_path', type=str, help='Path to the source PDF file')
    args = parser.parse_args()

    if not os.path.exists(args.pdf_path):
        print(f"Error: PDF file {args.pdf_path} not found.")
        sys.exit(1)

    # Step 1: Extract PDF text
    run_command(['python3', 'pdf_to_text.py', args.pdf_path])
    with open('extracted_text.txt', 'w', encoding='utf-8') as f:
        subprocess.run(['python3', 'pdf_to_text.py', args.pdf_path], stdout=f)

    # Step 2: Parse modules
    run_command(['python3', 'extract_data.py', '--input', 'extracted_text.txt', '--output', 'modules.json'])

    # Step 3: Compute embeddings + similarity
    run_command(['python3', 'analyze_similarity.py', '--input', 'modules.json', '--output', 'similarity_results.json'])

    # Step 4: Generate dashboard + PNGs
    run_command(['python3', 'create_dashboard.py', '--input', 'similarity_results.json', '--output', 'dashboard.html'])
    run_command(['python3', 'create_static_vis.py', '--input', 'similarity_results.json', '--map_output', 'module_map.png', '--heatmap_output', 'similarity_heatmap.png'])

    print("\n" + "="*50)
    print("Pipeline completed successfully!")
    print("Deliverables generated:")
    print("- modules.json (Extracted data)")
    print("- similarity_results.json (Similarity scores)")
    print("- dashboard.html (Interactive dashboard)")
    print("- module_map.png (Static semantic map)")
    print("- similarity_heatmap.png (Clustered heatmap)")
    print("="*50)

if __name__ == "__main__":
    main()
