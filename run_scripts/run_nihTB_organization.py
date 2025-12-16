import nihTB_data_processing_functions as nih  

RAW_DATA_DIR = 'datadump' 
OUTPUT_DIR = 'processed_subject_data'

def main():
    # Process ScoresExport csv files 
    print("\n Processing ScoresExport Files...")
    scores_df = nih.load_data_by_pattern(RAW_DATA_DIR, 'ScoresExport*.csv')
    
    if not scores_df.empty:
        # Save master scores file 
        nih.save_master_file(scores_df, OUTPUT_DIR, "MASTER_SCORES-NIHTB.csv")
        
        # split _scores by subject for individual folders
        nih.split_into_subject_folders(scores_df, OUTPUT_DIR, "_scores.csv")
    else:
        print("  - No summary dcore data found. Moving to ItemExport files.")


    # Process ItemExport csv files
    print("\n Processing ItemExport Files...")
    items_df = nih.load_data_by_pattern(RAW_DATA_DIR, 'ItemExport*.csv')
    
    if not items_df.empty:
        # Save master ItemExport file. Can be quite large.
        nih.save_master_file(items_df, OUTPUT_DIR, "MASTER_ITEMS-NIHTB.csv")
        
        # Split _items.csv by Subject
        nih.split_into_subject_folders(items_df, OUTPUT_DIR, "_items.csv")
    else:
        print("  - No trial buy trial data found.")
        
    print("\n **DATA PROCESSING COMPLETE**")

if __name__ == "__main__":
    main()