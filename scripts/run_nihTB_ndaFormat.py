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

# Map the output score names (right) with the data dictionary names (left)
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

# Visual reasoning has both v3.1 tag and a non-tagged version. To be safe, this task mapping was included so that it parses all instances of the task
TASK_MAPPING = {
    'Visual Reasoning': ['Visual Reasoning', 'Visual Reasoning v3.1', 'Visual Reasoningv3.1']
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
    """Extracts the core instrument name from the NDA definition."""
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
    
    # Task mappings are used for visual reasoning 
    if clean_target in TASK_MAPPING:
        matches = []
        possible_names = TASK_MAPPING[clean_target]
        for name in possible_names:
            if name in available_instruments_in_csv:
                matches.append(name)
        
        # If match found, return list 
        if matches:
            return matches

    # Find direct matches
    if clean_target in available_instruments_in_csv:
        return [clean_target]

    # Match between target and actual once strings removed
    target_simple = simplify_string(clean_target)
    
    for actual in available_instruments_in_csv:
        actual_simple = simplify_string(actual)
        if target_simple in actual_simple or actual_simple in target_simple:
            if "Form B" in actual and "Form A" in clean_target: # Make sure form B data is not included as it is not required by NDA
                continue
            return [actual] # Return as a single-item list
            
    return None

########################
#### MAIN EXECUTION ####
########################

def main():    
    df_data, df_dict = load_data()
    if df_data is None: return

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
        
        data_extract.append({
            'nda_var': target_var,
            'inst_key': instrument_key,
            'source_col': source_col_suffix
        })

    unique_instruments = df_data['InstrumentTitle'].dropna().unique()
    instrument_map = {} 
    
    print("\n  - Mapping Tasks...")
    for item in data_extract:
        key = item['inst_key']
        if key not in instrument_map:
            # List of strings 
            matches = find_instrument_match(key, unique_instruments)
            if matches:
                instrument_map[key] = matches
                if len(matches) > 1:
                     print(f"    [MATCH MULTI] Dict: '{key}' -> csv:  {matches}")
                else:
                     print(f"    [MATCH] Dict: '{key}' -> csv: '{matches[0]}'")
            else:
                instrument_map[key] = None
                print(f"    [!] NO MATCH for '{key}'")

    subjects = df_data['PID'].unique()
    extracted_data = {}

    # Sort index for performance
    df_indexed = df_data.set_index(['PID', 'InstrumentTitle']).sort_index()

    for item in data_extract:
        nda_var = item['nda_var']
        inst_key = item['inst_key']
        source_col = item['source_col']
        
        real_inst_names = instrument_map.get(inst_key) # This is now a list
        
        series_data = pd.Series(index=subjects, data=np.nan)

        if real_inst_names:
            try:
                # Match all names 
                subset = df_data[df_data['InstrumentTitle'].isin(real_inst_names)]
                
                if source_col in subset.columns:
                    # Group by PID and take the last entry if duplicate exists. shouldnt exist if organization script was run 
                    series_data = subset.groupby('PID')[source_col].last()
            except KeyError:
                pass
        
        extracted_data[nda_var] = series_data

    final_df = pd.DataFrame(extracted_data)
    final_df.index.name = 'subjectkey'
    final_df.reset_index(inplace=True)

    cols_ordered = ['subjectkey'] + [row['Variable_Name'] for _, row in df_dict.iterrows() if row['Variable_Name'] in final_df.columns]
    
    cols_ordered = [c for c in cols_ordered if c in final_df.columns]
    
    final_df = final_df[cols_ordered]
    
    final_df = final_df.fillna("")
    
    final_df.to_csv(OUTPUT_PATH, index=False)
    print(f"\n  [SUCCESS] NDA Formatted CSV file created: {OUTPUT_PATH}")
    print(f"  - Total Subjects: {len(final_df)}")
    print(f"  - Total Variables: {len(final_df.columns)}")

if __name__ == "__main__":
    main()