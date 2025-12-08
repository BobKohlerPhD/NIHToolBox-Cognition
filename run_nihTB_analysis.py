import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

##### Paths and task names #####
CSV_PATH = 'processed_subject_data/MASTER_SCORES-NIHTB.csv'
OUTPUT_BASE = 'processed_plots_and_descriptives'
TASK_COL = 'InstrumentTitle'

# Define the variables to analyze (Descriptives/Plots)
SCORE_VARIABLES = [
    'RawScore', 
    'TScore', 'TScoreStandardError', 
    'Theta', 'ThetaStandardError', 
    'ChangeSensitiveScore', 'ChangeSensitiveScoreStandardError', 
    'AgeAdjustedStandardScore', 'AgeAdjustedStandardScoreStandardError', 
    'AgeEduAdjustedTScore', 'AgeEduAdjustedTScoreStandardError', 
    'FullyAdjustedTScore',
    'NationalPercentileAgeAdjusted', 
    'ComputedScore', 
    'ItemCount'
]

##### Mappings for Error Definitions #####

# InstrumentBreakoff - Whether a test was interrupted #
#o 1 = Yes [Incomplete, early termination]
#o 2 = No [Completed, no early termination]
BREAKOFF_MAP = {1: 'Yes (Incomplete)', 2: 'No (Completed)'}

# InstrumentStatus2  - whether a test was administered #
#o 1 = Not Started
#o 2 = Partially Complete (i.e., test was stopped and can still be resumed)
#o 3 = Complete
#o 4 = Not Complete (i.e., test was interrupted or stopped by the examiner at a point where the test cannot be resumed)
STATUS_MAP = {1: 'Not Started', 2: 'Partially Complete', 3: 'Complete', 4: 'Not Complete'}

# InstrumentSandSReason variable definitions #
#o 1 = Environmental Issues
#o 2 = Cognitive Problems
#o 3 = Physical Limitations
#o 4 = Language Barrier
#o 5 = Participant Refused
#o -5 = Other
REASON_MAP = {1: 'Environmental', 2: 'Cognitive', 3: 'Physical', 4: 'Language', 5: 'Refused', -5: 'Other'}




##### Secondary Functions #####

def load_data(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"The file '{path}' was not found.")
    return pd.read_csv(path, low_memory=False)

def generate_error_summary(df, output_dir):

   # Generates an error summary CSV for the ENTIRE dataset.
    print("Generating Error Summary (error_summary.csv)")
    
    # Breakoff != 2 (No) OR Status != 3 (Complete)
    # using fillna(-1) ensures empty cells are counted as errors
    mask_errors = (df['InstrumentBreakoff'].fillna(-1) != 2) | (df['InstrumentStatus2'].fillna(-1) != 3)
    
    # Columns to keep (Look for PID or PIN)
    error_report_cols = [
        'PID', 
        'InstrumentTitle', 
        'InstrumentBreakoff', 
        'InstrumentStatus2', 
        'InstrumentSandSReason', 
        'InstrumentRCReasonOther', 
        'ParticipantNotes'
    ]
    
    existing_cols = [c for c in error_report_cols if c in df.columns]
    error_df = df.loc[mask_errors, existing_cols].copy()
    
    # Apply mappings from above 
    if 'InstrumentBreakoff' in error_df.columns:
        error_df['Breakoff_Desc'] = error_df['InstrumentBreakoff'].map(BREAKOFF_MAP)
    
    if 'InstrumentStatus2' in error_df.columns:
        error_df['Status_Desc'] = error_df['InstrumentStatus2'].map(STATUS_MAP)
        
    if 'InstrumentSandSReason' in error_df.columns:
        error_df['Reason_Desc'] = error_df['InstrumentSandSReason'].map(REASON_MAP)

    # Reorder columns
    final_cols = []
    for col in existing_cols:
        final_cols.append(col)
        if col == 'InstrumentBreakoff' and 'Breakoff_Desc' in error_df.columns:
            final_cols.append('Breakoff_Desc')
        elif col == 'InstrumentStatus2' and 'Status_Desc' in error_df.columns:
            final_cols.append('Status_Desc')
        elif col == 'InstrumentSandSReason' and 'Reason_Desc' in error_df.columns:
            final_cols.append('Reason_Desc')
            
    # Save
    if not error_df.empty:
        out_path = os.path.join(output_dir, 'error_summary.csv')
        error_df[final_cols].to_csv(out_path, index=False)
        print(f" -> '{len(error_df)} errors found. See error_summary.csv'.")
    else:
        print(" -> No errors.")

##### Main function #####

def analyze_instruments(df, output_dir):

   #  Main function for descriptive stats and plotting
    if TASK_COL not in df.columns:
        print(f"Error: Column '{TASK_COL}' not found.")
        return

    # All unique tasks (v3.1 vs no v3.1 tag)
    all_tasks = df[TASK_COL].dropna().unique()
    # Sort alphabetically
    all_tasks.sort()

    print(f"Found {len(all_tasks)} unique tasks.")

    for instrument in all_tasks:
        subset = df[df[TASK_COL] == instrument]
        
        if subset.empty:
            continue
        
        # Sanitize folder name
        safe_name = "".join([c for c in instrument if c.isalpha() or c.isdigit() or c==' ']).strip()
        target_dir = os.path.join(output_dir, safe_name)
        os.makedirs(target_dir, exist_ok=True)

        stats_file_path = os.path.join(target_dir, f'{safe_name}_Descriptives.txt')
        
        with open(stats_file_path, 'w') as f:
            f.write(f"Descriptive Statistics for: {instrument}\n")
            f.write("="*60 + "\n\n")

            for var in SCORE_VARIABLES:
                if var not in df.columns:
                    f.write(f"{var} -> NOT FOUND.\n" + "-"*30 + "\n")
                    continue

                # Force Numeric
                series_raw = subset[var]
                series_numeric = pd.to_numeric(series_raw, errors='coerce')
                
                nan_count = series_numeric.isna().sum()
                clean_series = series_numeric.dropna()
                
                valid_count = len(clean_series)
                total_rows = len(subset)

                # Write Stats
                f.write(f"Variable: {var}\n")
                f.write(f"  > Total Rows:    {total_rows}\n")
                f.write(f"  > Valid Data:    {valid_count} ({(valid_count/total_rows)*100:.1f}%)\n")
                f.write(f"  > Missing/NaN:   {nan_count}\n")
                
                if valid_count > 0:
                    f.write("\n  [Descriptives of Valid Data]\n")
                    desc = clean_series.describe().to_string().replace('\n', '\n    ')
                    f.write(f"    {desc}")
                else:
                    f.write("  [No valid data to calculate statistics]")

                f.write("\n" + "-"*30 + "\n")

                # Plotting
                if valid_count > 1 and clean_series.nunique() > 1:
                    try:
                        plt.figure(figsize=(10, 6))
                        sns.histplot(clean_series, kde=True, color='skyblue')
                        plt.title(f'{instrument}\nDistribution of {var}\n(Valid N={valid_count})')
                        plt.xlabel(var)
                        plt.ylabel('Frequency')
                        plt.tight_layout()
                        
                        plot_filename = f"{safe_name}_{var}_hist.png"
                        plt.savefig(os.path.join(target_dir, plot_filename))
                        plt.close()
                    except Exception as e:
                        print(f"Could not plot {var}: {e}")
                        plt.close()


##### Execution #####

if __name__ == "__main__":
    os.makedirs(OUTPUT_BASE, exist_ok=True)
    
    try:
        main_df = load_data(CSV_PATH)
        
        # 1. Generate Error Report (Includes ALL instruments)
        generate_error_summary(main_df, OUTPUT_BASE)
        
        # 2. Analyze Instruments (Includes ALL instruments)
        analyze_instruments(main_df, OUTPUT_BASE)
        
        print("\nScript has finished successfully.")
        
    except Exception as e:
        print(f"\ Error: {e}")