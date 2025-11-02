Apache JIRA Data Scraping & LLM Dataset Pipelin
Overview
This project implements a data scraping and transformation pipeline that extracts public issue data from Apache’s JIRA instance and converts it into a structured JSONL dataset suitable for Large Language Model (LLM) training.

It demonstrates how to design an efficient, fault-tolerant, and scalable scraping system capable of handling real-world data inconsistencies, API rate limits, and transformation challenges.


 Objective
Build a system that:
1. Scrapes issue data (title, description, comments, and metadata) from three Apache projects.
2. Handles network errors, pagination, and incomplete data gracefully.
3. Converts the scraped data into a high-quality, instruction-based JSONL corpus for LLM training.
4. Ensures reliability through checkpoints, retry logic, and structured output generation.



Architecture Overview

 📂 System Components
| Module | Description |
|---------|--------------|
| `scraper/` | Handles API communication, pagination, and checkpoint-based JIRA issue scraping. |
| `transformer/` | Cleans, normalizes, and converts raw JIRA JSON data into JSONL LLM-friendly format. |
| `run_pipeline.py` | Orchestrates both scraper and transformer stages. |
| `data/` | Stores raw issue JSONs (downloaded from JIRA). |
| `output/` | Contains transformed `.jsonl` datasets and logs. |


 Pipeline Flow


    A[Start] --> B[Scrape Issues from Apache JIRA API]
    B --> C[Save Raw JSONs to data/raw/]
    C --> D[Load Config and Checkpoints]
    D --> E[Transform Raw JSONs to Instruction Dataset]
    E --> F[Generate training_data.jsonl]
    F --> G[Output Metadata & Logs]
    G --> H[End]


⚙️ Setup & Installation
1️. Clone the Repository
bash
Copy code
git clone https://github.com/Sahej200/jira-project.git
cd jira-llm-pipeline

2️. Create Virtual Environment
Windows (PowerShell):
python -m venv .venv
.venv\Scripts\activate


3️. Install Dependencies
pip install -r requirements.txt



Usage
 1. Run Full Pipeline
python run_pipeline.py


This will:

Scrape the configured JIRA projects.

Transform and save the dataset to output/training_data.jsonl.

 2.  Run Only the Scraper
python -m scraper.jira_scraper

3. Run Only the Transformer
python -m transformer.data_transformer



Interactive CLI App — `app.py`

The `app.py` file adds an interactive command-line interface (CLI) layer on top of the pipeline.  
It allows users to control the entire workflow, check statuses, and view scraping summaries without typing long commands.

---

  Features
- Interactive menu-based control 
  Navigate between scraping, transforming, and viewing outputs easily.
- Live progress display
  Shows how many issues are scraped or transformed in real-time.
- Smart error handling  
  Automatically detects missing config, YAML errors, or API connection issues.
- Re-runs pipeline safely 
  Prevents accidental overwrites and resumes from checkpoints if needed.
- Shows dataset statistics  
  Displays number of raw files, total transformed examples, and output size.


... Run the App

Once your virtual environment is active, start the CLI interface using:
python app.py
You’ll see an interactive prompt like:

====================================
   Jira LLM Pipeline - Main Menu
====================================
1. Run full pipeline (Scraper + Transformer)
2. Run only Scraper
3. Run only Transformer
4. View scraping statistics
5. Exit


Made by - Sahej Prakash
e22cseu0725@bennett.edu.in
