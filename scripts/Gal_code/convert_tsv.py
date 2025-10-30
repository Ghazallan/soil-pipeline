import os
import shutil

# Path to your input directory
input_dir = r"C:\Users\hadis\OneDrive\Documents\Project\Ga_output\MetaphlanOutput.rocrate\relative_abundances"
output_dir = os.path.join(input_dir, "tsv_converted")

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Loop through all files in the input directory
for filename in os.listdir(input_dir):
    if filename.endswith(".tabular") or filename.endswith(".txt") or "Predicted_taxon_relative_abundances" in filename:
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, os.path.splitext(filename)[0] + ".tsv")
        
        # Copy file and rename extension (MetaPhlAn tabular files are already tab-delimited)
        shutil.copyfile(input_path, output_path)
        print(f"Converted: {filename} → {os.path.basename(output_path)}")

print("✅ Conversion complete! All .tsv files saved in:", output_dir)
