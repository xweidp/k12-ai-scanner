# K-12 AI Resource Scanner

A self-contained browser app for discovering and filtering K-12 education datasets, benchmarks, and models that can be used to evaluate and improve AI systems in classroom settings.

Open `index.html` in a browser to use it. No install step is required.

## Features

- **Filter by resource type**: Datasets, benchmarks, models, competitions
- **Filter by subject**: Math, science, reading, literacy, tutoring, assessment, and more
- **Filter by grade band**: Elementary, middle school, high school, K-12
- **Filter by license**: Open licenses only
- **Filter by modality**: Tabular, image, text, transcript, audio, video
- **Search**: Paste resource names or keywords to search the curated list
- **Export**: Download matching resources as CSV
- **Auto-refresh**: The scanner runs weekly and pulls fresh resources from curated sources

## Data Sources

The scanner pulls from:

1. **K-12 AI Infrastructure Program** (catalog) — Curated datasets and benchmarks for K-12 AI evaluation
2. **DrivenData Competitions** (monitor) — Data science competitions relevant to education
3. **Learning Commons** (monitor) — Open infrastructure for connecting research to classrooms
4. **Hugging Face** (monitor) — Education-focused datasets and models
5. **Linguistic Data Consortium** (monitor) — Language and annotation corpora for educational NLP

See [ADDING_SOURCES.md](ADDING_SOURCES.md) for how to add new sources.

## Resource Metadata

Each resource includes:

- **Title**: Name of the dataset, benchmark, or model
- **Type**: Dataset, Benchmark, Model, or Competition
- **Source**: Host organization (Stanford, UC Berkeley, etc.)
- **Subjects**: Inferred tags (Math, Science, Reading, Literacy, Tutoring, Assessment, etc.)
- **Grade Band**: Elementary, middle school, high school, or K-12 (unspecified)
- **Modality**: Data format (Tabular, Image, Text, Transcript, Audio, etc.)
- **License**: Usage restrictions (open, CC BY, proprietary, etc.)
- **Fit Score**: Relevance to K-12 AI education (0–100)

## Auto-Scan Setup

The app refreshes weekly via GitHub Actions + Netlify. See [AUTO_SCAN_SETUP.md](AUTO_SCAN_SETUP.md) for details on deployment.
