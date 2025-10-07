from bioblend.galaxy import GalaxyInstance
import glob
import os
import time
import re

# ------------------------------
# 1. Connect to Galaxy
# ------------------------------
GALAXY_URL = "https://usegalaxy.eu/"
API_KEY = "5f59788da0ca1fe9a3888de0beade579"  

gi = GalaxyInstance(GALAXY_URL, key=API_KEY)

# ------------------------------
# 2. Set directories
# ------------------------------
raw_dir = "/project/def-yuezhang/hazad25/project/raw_sample"
output_dir = "/project/def-yuezhang/hazad25/project/results/metaphlan_output"
os.makedirs(output_dir, exist_ok=True)

# ------------------------------
# 3. Find FASTQ pairs
# ------------------------------
fastqs = sorted(glob.glob(os.path.join(raw_dir, "*.fastq")))
pairs = {}

for f in fastqs:
    # Extract sample name (everything before _R1 or _R2)
    base = re.sub(r"_R[12]\.fastq$", "", os.path.basename(f))
    if base not in pairs:
        pairs[base] = {"R1": None, "R2": None}
    if "_R1" in f:
        pairs[base]["R1"] = f
    elif "_R2" in f:
        pairs[base]["R2"] = f

print(f"🧾 Found {len(pairs)} paired samples: {list(pairs.keys())}")

# ------------------------------
# 4. Find MetaPhlAn Tool
# ------------------------------
print("🔍 Searching for MetaPhlAn tool...")
tools = gi.tools.get_tools(name="MetaPhlAn")
if not tools:
    raise ValueError("❌ MetaPhlAn tool not found on this Galaxy instance.")
metaphlan_tool_id = tools[0]["id"]
print(f"⚙️ Using tool: {tools[0]['name']} ({metaphlan_tool_id})")

# ------------------------------
# 5. Define monitoring function
# ------------------------------
def monitor_history(gi, history_id, sample_name):
    """Wait until all datasets in a history are complete."""
    print(f"⏳ Monitoring MetaPhlAn job for {sample_name}...")
    while True:
        datasets = gi.histories.show_history(history_id, contents=True)
        states = [d["state"] for d in datasets]
        if all(s in ["ok", "error"] for s in states):
            break
        print(f"  Current dataset states: {states}")
        time.sleep(60)
    print(f"✅ MetaPhlAn job finished for {sample_name}")

# ------------------------------
# 6. Run MetaPhlAn for each sample pair
# ------------------------------
for sample, files in pairs.items():
    if not files["R1"] or not files["R2"]:
        print(f"⚠️ Skipping {sample} — missing R1 or R2")
        continue

    print(f"\n🚀 Processing sample: {sample}")

    # Create new history per sample
    history = gi.histories.create_history(name=f"{sample}_MetaPhlAn")
    print(f"🧬 Created history: {history['name']} ({history['id']})")

    # Upload both reads
    print(f"📤 Uploading {files['R1']} and {files['R2']}")
    up_R1 = gi.tools.upload_file(files["R1"], history["id"])
    up_R2 = gi.tools.upload_file(files["R2"], history["id"])
    r1_id = up_R1["outputs"][0]["id"]
    r2_id = up_R2["outputs"][0]["id"]

    # Prepare MetaPhlAn input
    # Adjust parameter names to match tool definition on your Galaxy instance
    inputs = {
        "input_reads": [
            {"src": "hda", "id": r1_id},
            {"src": "hda", "id": r2_id}
        ],
        # Optional: add params like number of threads or database version here
        # "nproc": "8",
        # "database": "mpa_vJan21_CHOCOPhlAnSGB_202103"
    }

    # Run MetaPhlAn
    print(f"🧩 Running MetaPhlAn on sample: {sample}")
    run = gi.tools.run_tool(history["id"], metaphlan_tool_id, inputs)
    job_id = run["jobs"][0]["id"]
    print(f"🧠 Submitted job ID: {job_id}")

    # Monitor job completion
    monitor_history(gi, history["id"], sample)

    # Download results
    print(f"⬇️ Downloading results for {sample}")
    datasets = gi.histories.show_history(history["id"], contents=True)
    sample_outdir = os.path.join(output_dir, sample)
    os.makedirs(sample_outdir, exist_ok=True)

    for ds in datasets:
        if ds["state"] == "ok":
            safe_name = ds["name"].replace(" ", "_").replace("/", "_")
            output_path = os.path.join(sample_outdir, f"{safe_name}.dat")
            print(f"   ⬇️ {ds['name']} → {output_path}")
            gi.datasets.download_dataset(
                ds["id"],
                file_path=output_path,
                use_default_filename=False,
                wait_for_completion=True
            )

    print(f"📁 Results saved in: {sample_outdir}")

print("\n🎉 All MetaPhlAn jobs completed successfully!")
print(f"Results directory: {output_dir}")
