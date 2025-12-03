# NIH Cognitive Toolbox Data Organizer

## Overview
This set of functions organizes datafiles exported from the **NIH Cognitive Toolbox Assessment Battery**. Scripts were created based on output from tasks delivered via ipadOS. 

The script `nihTB_organization.py` automates the organization and processing of CSV exports for both summary score and raw item outputs. All csv files can be placed in a folder named `datadump`

## Directory Structure

The script expects the following structure and will generate a `processed_subject_data` folder automatically that contains individual subdirectories for each participant. 

```text
.
├── datadump/                     # Place all raw CSV files here (looks for 'ScoresExport*.csv')
├── processed_subject_data/       # Script auto-generates this folder with sub-folders for each participant
├── nihTB_data_processing_functions.py
└── run_pipeline.py
```

Within each participant folder, two CSV files are generated:

```text
├── processed_subject_data/ 
    ├── subjectid/
       ├── subjectnumber_items.csv
       ├── subjectnumber_scores.csv
```
