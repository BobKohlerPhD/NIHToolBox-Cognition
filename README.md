Set of functions to organize datafiles that are exported from the NIH Cognitive Toolbox assessment battery delivered via ipadOS


This project automates the organization and processing of NIH Toolbox iPad data (v3). It takes raw CSV exports from multiple Research Assistants, cleans them, and organizes them into a research-ready directory structure.

Directory Structure

datadump/
Place all raw CSV files here. The script looks for any file matching ScoresExport*.csv.

Script auto-generates processed_subject_data/ folder that contains sub-folders for each participant

nihTB_data_processing_functions.py
Script containing the logic and functions currently implemented for organizing and processing data. 

run_pipeline.py
Script for executing functions. Run this file to start organization.

Setup requires python 3 and pandas library
