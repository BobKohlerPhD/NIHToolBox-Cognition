import pandas as pd
import os
import glob

def load_all_data(input_dir):
    # Looks for ALL files starting with 'ScoresExport' and ending in '.csv' within the input_dir specified 
    # This allows multiple RAs to send .csv datafiles that can be placed into a single folder 
    search_path = os.path.join(input_dir, 'ScoresExport*.csv')
    
    files = glob.glob(search_path)
    
    if not files:
        print(f"No files found in: {search_path}")
        print("Make sure .csv files are in the 'datadump' folder.")
        return pd.DataFrame()
    
    print(f"Found {len(files)} files.")
    dfs = []
    for f in files:
        try:
            temp_df = pd.read_csv(f)
            dfs.append(temp_df)
            print(f"  - Files Loaded: {os.path.basename(f)}")
        except Exception as e:
            print(f"  ! Error reading {f}: {e}")
            
    if not dfs:
        return pd.DataFrame()

    # Combine all into one DataFrame
    combined_df = pd.concat(dfs, ignore_index=True)
    
    # Remove exact duplicates from cumulative exports or if the same file was sent and added to data dump folder twice
    combined_df.drop_duplicates(inplace=True)
    
    return combined_df

def create_subject_folders(df, output_dir):
    # Create a directory for each subject for data split
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    unique_pids = df['PID'].unique()
    
    for pid in unique_pids:
        # Create directory structure: NIH_CognitiveTB/processed_subject_data/SUBJECT#/
        pid_clean = str(pid).strip()
        # Skip any NA or empty ID columns 
        if not pid_clean or pid_clean.lower() == 'nan':
            continue
            
        subject_dir = os.path.join(output_dir, pid_clean)
        
        # make directory if it doesnt exist but add check to see
        os.makedirs(subject_dir, exist_ok=True)

        # Extract rows for each subject
        subject_data = df[df['PID'] == pid]
        
        # Save individual CSV files in a participants directory. Will overwrite an existing file so that it has most up to date information
        save_path = os.path.join(subject_dir, f'{pid_clean}_raw_scores.csv')
        subject_data.to_csv(save_path, index=False)

    print(f"  - Data has been updated for {len(unique_pids)} subjects.")

