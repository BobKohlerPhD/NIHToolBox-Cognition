# NIH Cognitive Toolbox Data Organizer

## Overview
This set of functions organizes datafiles exported from the **NIH Cognitive Toolbox Assessment Battery**. Scripts were created based on output from tasks delivered via ipadOS. 

The script `run_nihTB_organization.py` automates the organization and processing of CSV exports for both summary score and raw item outputs. All csv files can be placed in a folder named `datadump/` that is CREATED BY THE USER.

Because the data contains timestamps, duplicate rows can be removed. The script `run_nihTB_organization.py` is designed to retain the only the first instance of duplicate data for the individual and master CSV files that are generated.

Windows OS executable files for both `run_nihTB_organization.py` and `run_nihTB_verify.py` are available for users who do not have python installed locally.

## Directory Structure
The script will generate a `processed_subject_data` folder automatically that contains individual subdirectories for each participant. The folder `datadump/` MUST BE CREATED BY THE USER and should contain all raw exported CSV files.

```text
├── datadump/                             # Place all raw CSV files here (looks for 'ItemExports*.csv' and 'ScoresExport*.csv')
├── processed_subject_data/               # Script auto-generates this folder with sub-folders for each participant
├── nihTB_data_processing_functions.py    # Functions called when running `run_nihTB_organization`
├── run_nihTB_organization.py             # Primary script that is run in terminal 
└── run_nihTB_verify.py                   # Verification script that is run in terminal after organization script is run
```

Within each participant folder, two CSV files are generated:

```text
├── processed_subject_data/
│   ├── sub-001/
│   │   ├── sub-001_scores.csv
│   │   └── sub-001_items.csv
│   └── sub-002/
│       ├── sub-002_scores.csv
│       └── sub-002_items.csv
```

## Verify New Data Files

The script `run_nihTB_verify.py` will compare the newly generated CSV files for each participant with their data contained in the raw files that were added to the `datadump/` folder. 
