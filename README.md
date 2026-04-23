# Academic Module Similarity Analysis

## Project Overview

This project provides a comprehensive solution for analyzing academic module descriptors from a PDF document to identify semantic similarities between modules and their learning outcomes. It generates interactive and static visualizations to help understand the relationships and overlaps across a degree programme.

## Features

*   **PDF Text Extraction**: Robust extraction of text from PDF documents, handling structured and semi-structured content.
*   **Module Data Parsing**: Intelligent parsing of extracted text to identify and categorize module information such as title, code, aims, learning outcomes, and indicative content.
*   **Semantic Similarity Analysis**: Utilizes state-of-the-art sentence embeddings (from `sentence-transformers`) to capture contextual meaning and quantify semantic resemblance between modules.
*   **Interactive Visualizations**: Generates an interactive HTML dashboard with:
    *   **Semantic Module Map (T-SNE)**: A 2D projection of module embeddings, clustering similar modules together.
    *   **Similarity Heatmap**: A visual representation of pairwise module similarities.
    *   **Top Overlapping Modules Table**: Highlights modules with the highest similarity scores, providing actionable insights.
*   **Static Visualizations**: Provides static PNG images of the T-SNE map and a clustered similarity heatmap for easy inclusion in reports.
*   **Pipeline Automation**: A single wrapper script to execute the entire analysis workflow from PDF input to visualization output.

## File Structure

The project consists of the following files:

*   `README.md`: This file, providing an overview of the project.
*   `requirements.txt`: Lists all Python dependencies required to run the project.
*   `run_pipeline.py`: The main script to execute the entire analysis pipeline.
*   `pdf_to_text.py`: Handles the conversion of the input PDF document into raw text.
*   `extract_data.py`: Parses the raw text to extract structured module information and saves it to `modules.json`.
*   `analyze_similarity.py`: Computes semantic similarity between modules using NLP techniques and generates `similarity_results.json`.
*   `create_dashboard.py`: Generates the interactive `dashboard.html` and individual plot HTML files (`module_map_plot.html`, `similarity_heatmap_plot.html`).
*   `create_static_vis.py`: Creates static PNG images of the T-SNE map (`module_map.png`) and the clustered similarity heatmap (`similarity_heatmap.png`).
*   `explanation.md`: A detailed document explaining the approach, design choices, and trade-offs made in the project.
*   `modules.json`: (Output) Contains the extracted structured data for all modules.
*   `similarity_results.json`: (Output) Stores the calculated similarity matrix and pairwise similarities.
*   `dashboard.html`: (Output) The interactive HTML dashboard.
*   `module_map_plot.html`: (Output) Self-contained HTML for the T-SNE plot.
*   `similarity_heatmap_plot.html`: (Output) Self-contained HTML for the heatmap plot.
*   `module_map.png`: (Output) Static PNG image of the T-SNE map.
*   `similarity_heatmap.png`: (Output) Static PNG image of the clustered similarity heatmap.

## Installation

To set up the project locally, follow these steps:

1.  **Clone the repository** (if applicable, otherwise ensure all project files are in one directory).

2.  **Ensure Python 3.8+ is installed** on your system.

3.  **Install the required Python packages** using `pip` and the provided `requirements.txt` file:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

To run the module similarity analysis pipeline, execute the `run_pipeline.py` script from your terminal, providing the path to your PDF document containing the module descriptors:

```bash
python3 run_pipeline.py /path/to/your/Data.pdf
```

Replace `/path/to/your/Data.pdf` with the actual path to your input PDF file.

## Deliverables

Upon successful execution, the following output files will be generated in your current working directory:

*   `dashboard.html`: An interactive HTML dashboard. Open this file in a web browser to explore the module similarities dynamically.
*   `module_map.png`: A static image of the semantic module map.
*   `similarity_heatmap.png`: A static image of the clustered similarity heatmap.
*   `modules.json`: The raw extracted module data.
*   `similarity_results.json`: The detailed similarity scores.

## Approach and Design Choices

For a detailed explanation of the project's approach, design choices, trade-offs, and validation metrics, please refer to the `explanation.md` document.
=======

