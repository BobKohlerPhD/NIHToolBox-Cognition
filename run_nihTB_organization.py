import nihTB_data_processing_functions as nih  
# --- CONFIGURATION ---
# Path to the folder containing your raw ScoresExport CSVs
RAW_DATA_DIR = 'datadump'  
# Path where the organized subject folders will be created
OUTPUT_DIR = 'processed_subject_data' 

def main():

    # Load Data
    full_data = nih.load_all_data(RAW_DATA_DIR)
    
    if full_data.empty:
        print("No data found.")
        return

    # Create individual subject Folders
    nih.create_subject_folders(full_data, OUTPUT_DIR)

if __name__ == "__main__":
    main()
