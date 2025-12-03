import pandas as pd
import os
import glob

def load_data_by_pattern(input_dir, file_pattern):
    #Function to load CSV files matching a pattern of 'ScoresExport*.csv' or 'ItemExport*.csv').
    search_path = os.path.join(input_dir, file_pattern)
    files = glob.glob(search_path)
    
    if not files:
        print(f"  [!] No files found matching: {file_pattern}")
        return pd.DataFrame()
    
    print(f"  - Found {len(files)} files matching '{file_pattern}'.")
    dfs = []
    for f in files:
        try:
            temp_df = pd.read_csv(f, low_memory=False) 
            dfs.append(temp_df)
        except Exception as e:
            print(f"  ! Error reading {f}: {e}")
            
    if not dfs:
        return pd.DataFrame()

    combined_df = pd.concat(dfs, ignore_index=True)
    combined_df.drop_duplicates(inplace=True)
    
    return combined_df

def save_master_file(df, output_dir, filename):

    #Saves the master dataframe to the output directory.
    if df.empty:
        return
        
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    master_path = os.path.join(output_dir, filename)
    df.to_csv(master_path, index=False)
    print(f"  - Master data file saved: {filename}")

def split_into_subject_folders(df, output_dir, file_suffix):

   # Splits the dataframe by 'PID' and saves individual files. File_suffixes are '_scores.csv' and '_items.csv'

    if df.empty:
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    unique_pids = df['PID'].unique()
    total_rows = len(df)
    
    count = 0
    for pid in unique_pids:
        pid_clean = str(pid).strip()
        if not pid_clean or pid_clean.lower() == 'nan':
            continue
            
        # Create subject folder
        subject_dir = os.path.join(output_dir, pid_clean)
        os.makedirs(subject_dir, exist_ok=True)

        # Filter data for this subject
        subject_data = df[df['PID'] == pid]
        
        # Save file with specific suffix
        save_path = os.path.join(subject_dir, f'{pid_clean}{file_suffix}')
        subject_data.to_csv(save_path, index=False)
        count += 1

    print(f"  - Processed {count} subjects for {file_suffix} (Rows: {total_rows})")