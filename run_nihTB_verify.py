import pandas as pd
import pandas.testing as pdt
import os

# Match OUTPUT_DIR here with OUTPUT_DIR in 'run_nihTB_organization.py' script 
OUTPUT_DIR = 'processed_subject_data' 

def verify_dataset(master_filename, suffix, id_col='PID'):
    print(f"\n--- Verifying {master_filename} against individual *{suffix} files ---")
    
    master_path = os.path.join(OUTPUT_DIR, master_filename)
    if not os.path.exists(master_path):
        print(f"  [Skipping] Master file not found: {master_filename}")
        return

    print(f"  - Loading Master File...")
    # Read master file
    try:
        df_master = pd.read_csv(master_path, low_memory=False)
    except Exception as e:
        print(f"  [Error] Could not read master file: {e}")
        return

    # Standardize PID column for matching
    df_master['match_id'] = df_master[id_col].astype(str).str.strip()
    
    subject_dirs = [d for d in os.listdir(OUTPUT_DIR) if os.path.isdir(os.path.join(OUTPUT_DIR, d))]
    
    checked_count = 0
    errors = []
    
    print(f"  - Checking integrity for {len(subject_dirs)} subject folders...")

    for subj_id in subject_dirs:
        subj_file_name = f"{subj_id}{suffix}"
        subj_file_path = os.path.join(OUTPUT_DIR, subj_id, subj_file_name)
        
        if not os.path.exists(subj_file_path):
            continue
            
        # Load subject level data
        df_subj = pd.read_csv(subj_file_path, low_memory=False)
        
        # Filter master file to match subject
        df_master_subset = df_master[df_master['match_id'] == subj_id].copy()
        df_master_subset = df_master_subset.drop(columns=['match_id'])
        
        # Check row counts
        if len(df_subj) != len(df_master_subset):
            errors.append(f"Subject {subj_id}: Row count mismatch (Individual: {len(df_subj)}, Master: {len(df_master_subset)})")
            continue
            
        # Align columns
        df_master_subset = df_master_subset[df_subj.columns]
        
        # Reset index
        df_subj_reset = df_subj.reset_index(drop=True)
        df_master_reset = df_master_subset.reset_index(drop=True)
        
        # Harmonize data because of string vs. float mismatches (string "1.0" vs float 1.0)
        for col in df_subj_reset.columns:
            # Force to numeric
            is_subj_num = pd.api.types.is_numeric_dtype(df_subj_reset[col])
            is_mast_num = pd.api.types.is_numeric_dtype(df_master_reset[col])
            
            if is_subj_num != is_mast_num:
                # Convert both to numeric, errors to NaN. Ensures comparison of 1.0 to 1.0
                df_subj_reset[col] = pd.to_numeric(df_subj_reset[col], errors='coerce')
                df_master_reset[col] = pd.to_numeric(df_master_reset[col], errors='coerce')

        # MAIN CHECK FOR DATA #
        try:
            # check_dtype=False = Int vs Float comparison
            # check_exact=False = tiny floating point differences
            pdt.assert_frame_equal(df_subj_reset, df_master_reset, check_dtype=False, check_exact=False)
            checked_count += 1
        except AssertionError as e:
            errors.append(f"Subject {subj_id}: Data mismatch.\n    Details: {e}")

    # Final Report
    if not errors:
        print(f"  [SUCCESS] Verified {checked_count} subjects. All data matches.")
    else:
        print(f"  [FAILURE] Found mismatches for {len(errors)} subjects:")
        for e in errors[:5]: 
            print(f"    ! {e}")
        if len(errors) > 5:
            print(f"    ... and {len(errors)-5} more.")
def main():
    # Verify Scores
    verify_dataset('MASTER_SCORES-NIHTB.csv', '_scores.csv')
    
    # Verify Items 
    verify_dataset('MASTER_ITEMS-NIHTB.csv', '_items.csv')

if __name__ == "__main__":
    main()
