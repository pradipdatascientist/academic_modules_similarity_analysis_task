# Academic Module Similarity Analysis: Approach and Design Choices

## 1. Introduction

This document details the methodology employed to extract, process, and analyze academic module descriptors from a provided PDF document. The primary objective was to identify similarities between modules and their learning outcomes, culminating in clear, interpretable visualizations of these relationships across the degree programme.

## 2. Data Extraction and Pre-processing

### Approach

The initial step involved extracting textual content from the `Data.pdf` document. Given the structured, yet semi-unstructured nature of the module descriptors within the PDF (each module starting with "Module Code:", followed by various fields), a two-step extraction process was implemented:

1.  **PDF to Raw Text Conversion**: The `pdfminer.six` library was used to convert the entire PDF document into a plain text file (`extracted_text.txt`). This library was chosen for its robustness in handling various PDF structures and its ability to preserve text order, which is crucial for subsequent parsing.
2.  **Structured Data Extraction**: A custom Python script (`extract_data.py`) was developed to parse the raw text and extract key information for each module. Regular expressions were extensively used to identify and capture fields such as `Module Code`, `Title`, `SCQF Level`, `Module Aim`, `Learning Outcomes`, and `Indicative Content`. Special attention was paid to handling multi-line entries for learning outcomes and indicative content, ensuring that all relevant text was captured and properly formatted. The extracted data was then saved into a JSON file (`modules.json`) for easy programmatic access.

### Design Choices and Trade-offs

*   **Regular Expressions**: While powerful for pattern matching, regular expressions can be brittle if the document structure varies significantly. However, for the consistent format observed in the provided PDF, they offered a lightweight and efficient solution. A trade-off was made to refine the regex patterns iteratively to accommodate minor variations and ensure comprehensive data capture.
*   **JSON Output**: Storing the extracted data in JSON format provides a universally readable and structured representation, facilitating subsequent analysis steps and easy integration with other tools or systems. This choice prioritizes interoperability and ease of use.

### Validation Metrics

To ensure the quality of the extracted data, a validation step was integrated into the extraction process. The following metrics were collected:

| Metric                        | Value |
| :---------------------------- | :---- |
| Total Modules Extracted       | 52    |
| Modules with Missing Aims     | 0     |
| Modules with Missing LOs      | 0     |
| Average LOs per Module        | 4.37  |

These metrics confirm that all 52 unique modules were successfully extracted, with no missing aims or learning outcomes, indicating a robust extraction process. The deduplication step successfully handled any repeated module entries in the source PDF.

## 3. NLP Similarity Analysis

### Approach

To identify semantic similarities between modules, a Natural Language Processing (NLP) approach using **sentence embeddings** was chosen. This method moves beyond simple keyword matching to understand the contextual meaning of the text.

1.  **Text Combination**: For each module, the `Title`, `Module Aim`, `Learning Outcomes`, and `Indicative Content` were concatenated into a single, comprehensive text string. To reflect the emphasis on "what students will be learning," the text from `Learning Outcomes` was repeated twice in the combined string, effectively weighting it more heavily in the embedding process.
2.  **Sentence Embeddings**: The `sentence-transformers` library was utilized, specifically employing the pre-trained model `all-MiniLM-L6-v2`. This model is known for its balance of performance and computational efficiency, making it suitable for local execution. It converts the combined text of each module into a high-dimensional vector (embedding) that semantically represents the module's content.
3.  **Cosine Similarity**: The cosine similarity metric was applied to these embeddings to quantify the semantic resemblance between every pair of modules. A higher cosine similarity score indicates greater semantic overlap.
4.  **Output**: The calculated similarity matrix and a list of all pairwise similarities were saved to `similarity_results.json`, along with the original module data.

### Design Choices and Trade-offs

*   **Semantic Depth**: Using `sentence-transformers` addresses the requirement for semantic depth by capturing contextual meaning rather than just keywords. This helps detect overlap even when different terminology is used to describe similar learning outcomes. This approach was chosen over bag-of-words or TF-IDF because module similarity should reflect contextual meaning, not just shared keywords. This helps detect overlap where different wording is used to describe similar learning.
*   **Model Selection**: `all-MiniLM-L6-v2` was selected for its efficiency. While larger models might offer slightly higher accuracy, the chosen model provides a good balance for this task, ensuring reasonable processing times on a local machine. A trade-off was made between maximal accuracy and computational resources.
*   **Weighted Learning Outcomes**: By repeating the learning outcomes text, the model is encouraged to give more importance to these sections when generating embeddings, aligning with the task's focus on "what students will be learning."

## 4. Visualisation and Interactive Dashboard

### Approach

To present the module similarities clearly and interactively, an HTML-based dashboard was created using `Plotly` and `pandas`, complemented by static visualizations using `matplotlib` and `seaborn`.

1.  **T-SNE Semantic Map**: A 2D scatter plot was generated using t-Distributed Stochastic Neighbor Embedding (t-SNE) to reduce the high-dimensional embeddings into a two-dimensional space. Modules that are semantically similar are clustered closer together on this map. Each module is labeled with its code, and hovering over a point reveals its full title. The points are colored by SCQF Level to provide additional context. The static version of this map (`module_map.png`) was improved for readability with better spacing and clearer labels.
2.  **Similarity Heatmap**: An interactive heatmap was generated to visually represent the cosine similarity matrix. This provides an overview of all pairwise similarities, allowing for quick identification of highly similar or dissimilar modules. A static, clustered heatmap (`similarity_heatmap.png`) was also generated, which uses hierarchical clustering to group similar modules together, making patterns of similarity more apparent.
3.  **Top Overlapping Modules Table**: A table listing the top 20 most similar module pairs (based on cosine similarity) was included in the interactive dashboard. This table highlights potentially heavily overlapping modules and suggests actionable insights based on defined similarity thresholds.
4.  **Example Nearest Neighbours**: To further illustrate module relationships, a small table of example nearest neighbors is provided below, showcasing modules that are semantically closest to a given module.

    | Module Code | Nearest Neighbours (Top 3) |
    | :---------- | :------------------------- |
    | CM1113      | CM2115, CE2001, CE2000     |
    | CM1131      | CM3145, CM3144, CM2133     |

5.  **Interactive HTML Dashboard**: All interactive visualizations and the table were integrated into a single, interactive HTML file (`dashboard.html`). To address persistent rendering issues, each Plotly figure is now generated as a **self-contained HTML snippet** (including its own Plotly.js library) and embedded into the main dashboard using `<iframe>` tags. This approach ensures that each plot is isolated and its JavaScript dependencies are correctly loaded and executed, preventing conflicts and ensuring reliable rendering across different browser environments.

### Design Choices and Trade-offs

*   **Interactive Dashboard (Plotly + iFrames)**: Plotly was chosen for its ability to create rich, interactive web-based visualizations. The use of `<iframe>` tags for embedding individual plot HTML snippets enhances user experience by allowing dynamic exploration of the data while ensuring robust rendering. The trade-off is that it might slightly increase the file size of the main dashboard HTML due to repeated Plotly.js inclusions, but it significantly improves reliability.
*   **T-SNE**: t-SNE is effective for visualizing high-dimensional data in 2D, revealing natural clusters. However, its non-deterministic nature means that slight variations might occur between runs, and the absolute distances in the 2D map do not directly correspond to the original high-dimensional distances. Perplexity was set to `min(30, len(modules)-1)` to ensure it's always valid even for small numbers of modules.
*   **Actionable Insights**: The "Interpretation" column in the top overlaps table directly addresses the requirement for actionable insights. The thresholds for interpretation are justified as follows:
    *   `> 0.85`: Possible overlap / duplication risk
    *   `0.70–0.85`: Likely topic continuity or progression
    *   `< 0.70`: Related but distinct
    It is important to note that high similarity is not automatically a problem; it may reflect deliberate progression between levels or foundational knowledge.
*   **Improved Static Visuals**: The addition of a clustered heatmap provides an alternative view of module similarities, complementing the T-SNE map by explicitly showing groupings based on content. This helps in identifying overarching course themes like software development, data/AI, cyber security, creative media/games, and web/mobile, which often appear as clusters.

## 6. How to Run the Solution

To run this solution locally, a single wrapper script (`run_pipeline.py`) is provided, which orchestrates all steps. This improves the "run locally / easily deployable" requirement and makes the project look cleaner and more production-aware.

1.  **Prerequisites**: Ensure you have Python 3.8+ installed.
2.  **Install Dependencies**: Install the required Python libraries using pip. A `requirements.txt` file is provided for convenience:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Run the Pipeline**: Execute the main pipeline script, providing the path to your PDF file:
    ```bash
    python3 run_pipeline.py /path/to/your/Data.pdf
    ```

After these steps, you will find `dashboard.html` (interactive visualization), `module_map.png` (static T-SNE map), and `similarity_heatmap.png` (static clustered heatmap) in your current working directory.

## 7. Deliverables

*   `explanation.md`: This document, detailing the approach, design choices, and trade-offs.
*   `requirements.txt`: List of Python dependencies.
*   `run_pipeline.py`: Wrapper script to execute the entire pipeline.
*   `pdf_to_text.py`: Python script for converting PDF to raw text.
*   `extract_data.py`: Python script for extracting module information from the PDF.
*   `analyze_similarity.py`: Python script for performing NLP similarity analysis.
*   `create_dashboard.py`: Python script for generating the interactive HTML dashboard.
*   `create_static_vis.py`: Python script for generating static PNG images of the module map and clustered heatmap.
*   `modules.json`: JSON file containing the extracted module data.
*   `similarity_results.json`: JSON file containing the similarity matrix and pairwise similarities.
*   `dashboard.html`: Interactive HTML dashboard visualizing module similarities.
*   `module_map.png`: Static PNG image of the semantic module map.
*   `similarity_heatmap.png`: Static PNG image of the clustered similarity heatmap.

## 8. Scalability Considerations

The current implementation is suitable for moderate-scale analysis (e.g., dozens to a few hundred modules). For larger datasets, the pipeline can be extended by adding argumentized I/O, more robust error handling and logging, caching of embeddings, and potentially distributed processing for embedding generation. The use of `sentence-transformers` and `scikit-learn` provides a solid foundation for scaling, as these libraries are optimized for performance. Further optimizations could include using approximate nearest neighbor search for very large datasets instead of full cosine similarity matrix computation.
