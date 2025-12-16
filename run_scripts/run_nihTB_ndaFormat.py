import pandas as pd
import re
from pathlib import Path
import numpy as np

BASE_DIR = Path('.') # Current directory
INPUT_DATA_PATH = BASE_DIR / 'processed_subject_data/MASTER_SCORES-NIHTB.csv'
DICT_PATH = BASE_DIR / 'DataDictionary_NIHTB-COGNITION.csv' 
OUTPUT_PATH = BASE_DIR / 'Data-Full_NDAFormat.csv'

###########################
#### Variable Mappings ####
###########################

# Identify variable needed in dict_path and map it to standardized name
SCORE_TYPE_MAP = {
    'Age adjusted score standard error': 'AgeAdjustedStandardScoreStandardError',
    'Age adjusted score': 'AgeAdjustedStandardScore',
    'Change sensitive score standard error': 'ChangeSensitiveScoreStandardError',
    'Change sensitive score': 'ChangeSensitiveScore',
    'Computed score': 'ComputedScore',
    'Item count': 'ItemCount',
    'National Percentile Age Adjusted score': 'NationalPercentileAgeAdjusted',
    'Raw Score': 'RawScore',
    'Theta standard error': 'ThetaStandardError',
    'Theta': 'Theta',
    'T-score standard error': 'TScoreStandardError',
    'T-score': 'TScore',
    'Fully Adjusted T-score': 'FullyAdjustedTScore'
}

# Visual reasoning task has v3.1 tag and can cause issues when formatting. This catches any possible instance of it 
TASK_MAPPING = {
    'Visual Reasoning': ['Visual Reasoning', 'Visual Reasoning v3.1', 'Visual Reasoningv3.1']
}

# Some participants have Assessment 1 as their first "AssessmentName" and this will standardize naming to "Baseline" 
VISIT_LABEL_MAP = {
    'Assessment 1': 'Baseline',
    'Assessment1': 'Baseline',
    'assessment 1': 'Baseline',
    'Visit 1': 'Baseline'
}

#############################
#### Secondary Functions ####
#############################

def load_data():
    if not INPUT_DATA_PATH.exists():
        print(f"[ERROR] Input file not found: {INPUT_DATA_PATH}")
        return None, None
    
    df_data = pd.read_csv(INPUT_DATA_PATH, low_memory=False)
    df_dict = pd.read_csv(DICT_PATH)
    return df_data, df_dict

def clean_instrument_name(full_def_str):
    cleaned = full_def_str.replace('NIH Toolbox ', '')
    cleaned = re.split(r'v\d+\.\d+', cleaned)[0]
    sorted_score_keys = sorted(SCORE_TYPE_MAP.keys(), key=len, reverse=True)
    for score_type in sorted_score_keys:
        if cleaned.lower().endswith(score_type.lower()):
            cleaned = cleaned[:-(len(score_type))].strip()
            break
    return cleaned.strip()

def simplify_string(s):
    return s.lower().replace('test', '').replace('exam', '').replace(' ', '').replace('\xa0', '')

def find_instrument_match(target_name_from_dict, available_instruments_in_csv):
    clean_target = target_name_from_dict.strip()
    if clean_target in TASK_MAPPING:
        matches = []
        possible_names = TASK_MAPPING[clean_target]
        for name in possible_names:
            if name in available_instruments_in_csv:
                matches.append(name)
        if matches: return matches

    if clean_target in available_instruments_in_csv:
        return [clean_target]

    target_simple = simplify_string(clean_target)
    for actual in available_instruments_in_csv:
        actual_simple = simplify_string(actual)
        if target_simple in actual_simple or actual_simple in target_simple:
            if "Form B" in actual and "Form A" in clean_target: 
                continue
            return [actual]
            
    return None

def standardize_visit_labels(df):
    eventname_col = ['AssessmentName']
    target_col = None
    
    for col in eventname_col:
        if col in df.columns:
            target_col = col
            break
    
    if target_col:
        print(f"  - Standardizing visit names from column: '{target_col}'")
        df[target_col] = df[target_col].replace(VISIT_LABEL_MAP)
        return df, target_col 
    else:
        print("  - [INFO] No explicit Timepoint/Session column found to normalize.")
        return df, None

########################
#### MAIN EXECUTION ####
########################
def main():    
    df_data, df_dict = load_data()
    if df_data is None: return

    # Use standardize label function 
    df_data, visit_col = standardize_visit_labels(df_data)

    # 
    date_col = 'DateFinished'
    if date_col not in df_data.columns:
        if 'ResponseDate' in df_data.columns:
            date_col = 'ResponseDate'
        else:
            print("[ERROR] Could not find 'DateFinished' variable. Groupings could be inaccurate.")
            date_col = None 

    # Remove time from datefinished so only data is present. Since tasks are completed on the same time, exact time is irrelevant and a date does not need to be created for each individual task 
    if date_col:
        print(f"  - Normalizing timestamps in column: '{date_col}'")
        # Convert to utc to avoid weird issues 
        df_data[date_col] = pd.to_datetime(df_data[date_col], errors='coerce', utc=True)
        # Forces all times to 00:00:00 so that the date can be safely removed 
        df_data[date_col] = df_data[date_col].dt.normalize()

    # Pull what is needed from df_dict based on columns in file 
    data_extract = []
    
    for idx, row in df_dict.iterrows():
        target_var = row['Variable_Name']
        definition = str(row['definition'])
        
        source_col_suffix = None
        sorted_score_keys = sorted(SCORE_TYPE_MAP.keys(), key=len, reverse=True)
        
        for score_desc in sorted_score_keys:
            if score_desc.lower() in definition.lower():
                source_col_suffix = SCORE_TYPE_MAP[score_desc]
                break
        
        if not source_col_suffix:
            continue
            
        instrument_key = clean_instrument_name(definition)
        
        #Get: nda variable; instrument name; column definition in data_dict -> actual column name needed in NDA formatted CSV
        # This ensures the right data is taken since the same variables are present for all tasks in a raw CSV 
        # Example: { 'nda_var': 'nihtbx_flanker_raw',  'inst_key': 'Flanker',  'source_col': 'RawScore' }
        data_extract.append({
            'nda_var': target_var, # what should name of the task be in file 
            'inst_key': instrument_key, # which row(s) are associated with this task name 
            'source_col': source_col_suffix # what values in the row should be copied over for that task 
        })

    unique_instruments = df_data['InstrumentTitle'].dropna().unique()
    instrument_map = {} 
    
    # Loop through data and fill data_extract[] created above 
    print("\n  - Mapping Tasks...")
    for item in data_extract:
        key = item['inst_key']
        if key not in instrument_map:
            matches = find_instrument_match(key, unique_instruments)
            if matches:
                instrument_map[key] = matches
            else:
                instrument_map[key] = None

    extracted_data = {}

    # Take the multiple AssessmentName rows per participant (I.e., Assessment 1 Visual; Next row - Assessment 1 Picture) and condenses to 1 row per participant as 'eventname'
    if visit_col and date_col:
        try:
            extracted_data['eventname'] = df_data.groupby(['PID', date_col])[visit_col].last()
        except Exception:
            pass

    for item in data_extract:
        nda_var = item['nda_var']
        inst_key = item['inst_key']
        source_col = item['source_col']
        
        real_inst_names = instrument_map.get(inst_key)
        series_data = None 

        if real_inst_names:
            try:
                subset = df_data[df_data['InstrumentTitle'].isin(real_inst_names)].copy()
                if source_col in subset.columns:
                    # Group by PID date that has been normalized with time removed
                    if date_col and date_col in subset.columns:
                        series_data = subset.groupby(['PID', date_col])[source_col].last()
                    else:
                        series_data = subset.groupby('PID')[source_col].last()
            except KeyError:
                pass
        
        if series_data is not None:
            extracted_data[nda_var] = series_data

    final_df = pd.DataFrame(extracted_data)
    
    if date_col and isinstance(final_df.index, pd.MultiIndex):
        final_df.index.names = ['subjectkey', 'interview_date']
    else:
        final_df.index.name = 'subjectkey'
        
    final_df.reset_index(inplace=True)

    # Date formatting (XX/XX/XXXX)
    if 'interview_date' in final_df.columns:
        # timestamps were changed to 00:00:00 UTC in previous step, now just format data for NDA (XX/XX/XXXX)
        final_df['interview_date'] = final_df['interview_date'].dt.strftime('%m/%d/%Y')

    # Reorder cols
    dict_vars = [row['Variable_Name'] for _, row in df_dict.iterrows()]
    # Variables to keep at beginning of DF
    base_cols = ['subjectkey', 'interview_date', 'eventname'] 
    
    final_cols = [c for c in base_cols + dict_vars if c in final_df.columns]
    
    # Not sure if needed but will remove any duplicated columns. May become relevant with multiple timepoints
    seen = set()
    final_cols = [x for x in final_cols if not (x in seen or seen.add(x))]

    #Keep blank cells blank and don't let them convert to NaN for proper NDA formatting 
    final_df = final_df[final_cols].fillna("")
    
    final_df.to_csv(OUTPUT_PATH, index=False)
    print(f"\n NDA formatted CSV created and placed in: {OUTPUT_PATH}")
    print(f"  - Total rows included in NDA formatted CSV: {len(final_df)}")
    print(f"  - Total variables included in NDA formatted CSV: {len(final_df.columns)}")

if __name__ == "__main__":
    main()