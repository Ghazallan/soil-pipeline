import os
import re

# Path to your folder
folder_path = r"C:\Users\hadis\OneDrive\Documents\Project\Galaxy_output\MetaphlanOutput.rocrate\datasets"

# Mapping: Data ID → New File Name (sample name)
mapping = {
    "0a8d5244b05fb5305fbb2cf7336d5c54": "SCBI_012",
    "0a8d5244b05fb530a90aba8ebc133286": "ABBY_063",
    "0a8d5244b05fb530eaa852b57fd99525": "BARR_054",
    "0a8d5244b05fb5304b322da9826883a1": "BART_040",
    "0a8d5244b05fb530f2c2b41a5fc898e9": "CLBJ_001",
    "0a8d5244b05fb5304c53001790528b9e": "CPER_006",
    "0a8d5244b05fb5303ab4d39bec0bfba3": "GUAN_049",
    "0a8d5244b05fb5304a30fb7b312b283d": "HARV_035",
    "0a8d5244b05fb530044019af88c1527b": "JORN_004",
    "0a8d5244b05fb530df4d3f73ed8faaa6": "KONZ_042",
    "0a8d5244b05fb5303a7655324689c61d": "MOAB_045",
    "0a8d5244b05fb53022332ebd53dd47b4": "NIWO_001",
    "0a8d5244b05fb530bb8d821f1a26ffa4": "ONAQ_002",
    "0a8d5244b05fb5303bca0fdb3ed52976": "ORNL_043",
    "0a8d5244b05fb530dfcc2eef0762b02d": "OSBS_003",
    "0a8d5244b05fb530268068d39f33d6f8": "SCBI_003",
    "0a8d5244b05fb530e12fda43726a4cf2": "SJER_046",
    "0a8d5244b05fb5304af07ccc7c40bb66": "SRER_043",
    "0a8d5244b05fb53000d8ac5f3180d079": "STEI_002",
    "0a8d5244b05fb530d32298440c0238f1": "STER_027",
    "0a8d5244b05fb5302eead1a204c4e89e": "TOOL_005",
    "0a8d5244b05fb53081d8ed5510ff8352": "UNDE_038",
    "0a8d5244b05fb53060005b1b13f5def3": "WOOD_002",
    "0a8d5244b05fb53035a8f026ac111046": "WOOD_042",
    "0a8d5244b05fb530f6828021593445ce": "WREF_071",
    "0a8d5244b05fb530da11efae7bd656ce": "TALL_002",
    "0a8d5244b05fb5301ac2652f77eacb32": "PUUM_036",
    "0a8d5244b05fb5309836a82f0b7499d2": "BONA_009",
}

# Pattern to find a 32-character hexadecimal ID anywhere in the filename
pattern = re.compile(r"[a-f0-9]{32}")

# Process all files in the folder
for filename in os.listdir(folder_path):
    full_path = os.path.join(folder_path, filename)

    # Skip subdirectories
    if not os.path.isfile(full_path):
        continue

    match = pattern.search(filename)
    if not match:
        print(f"❌ No data ID found in: {filename}")
        continue

    data_id = match.group(0)

    # Check if the ID exists in our mapping
    if data_id not in mapping:
        print(f"⚠️ No mapping found for ID: {data_id} ({filename})")
        continue

    # Replace only the ID part with the sample name
    new_filename = filename.replace(data_id, mapping[data_id])
    new_full_path = os.path.join(folder_path, new_filename)

    # Avoid overwriting files
    if os.path.exists(new_full_path):
        print(f"⚠️ Skipped (target exists): {new_filename}")
        continue

    # Rename file
    os.rename(full_path, new_full_path)
    print(f"✅ Renamed:\n   {filename}\n   → {new_filename}\n")

print("\n🎉 Done renaming all matching files!")
