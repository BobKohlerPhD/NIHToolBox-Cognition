NIH Toolbox Data Preprocessing Pipeline

This project automates the organization and processing of NIH Toolbox iPad data (v3). It takes raw CSV exports from multiple Research Assistants, cleans them, and organizes them into a research-ready directory structure.

Directory Structure

datadump/
Place all raw CSV files here. The script looks for any file matching ScoresExport*.csv.

processed_subject_data/
The script auto-generates this folder. It contains:

Individual subject sub-folders (e.g., 1001/1001_raw_scores.csv).

Master_Dataset_Wide.csv (The final file for statistical analysis).

nihTB_dataprocess.py
The library file containing the logic and functions (load_all_data, generate_wide_dataset, etc.).

run_pipeline.py
The execution script. Run this file to start the job.

Setup

Install Python 3 (if not already installed).

Install the required libraries:

pip install pandas


Usage

Collect Data:
    et the .csv export files from your RAs.

Stage Data:
    Drop all ScoresExport_*.csv files into the datadump/ folder (Note: File naming doesn't matter as long as it starts with "ScoresExport" and ends in ".csv").

Run the Pipeline:
    Open a terminal in this folder and run:
        python run_pipeline.py


View Results:
    For Analysis: Open processed_subject_data/Master_Dataset_Wide.csv in Excel, SPSS, or R.
    For Archiving: Check the individual subject folders in processed_subject_data/.

Data Privacy Warning

Do not share the datadump or processed_subject_data folders publicly (e.g., on GitHub).
These folders contain Participant Health Information (PHI). Only share the .py scripts and this README.