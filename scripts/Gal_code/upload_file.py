from bioblend.galaxy import GalaxyInstance
import glob
import os
import time
import re

# ------------------------------
# 1. Connect to Galaxy
# ------------------------------
GALAXY_URL = "https://usegalaxy.org"
API_KEY = "ab7abad43988b720c5503ad0ca7aa415"

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
# 4. Get MetaPhlAn workflow
# ------------------------------
workflow_name = "Taxanomy_Metaphlan"  # must match your Galaxy workflow name
workflows = gi.workflows.get_workflows(name=workflow_name)
if not workflows:
    raise ValueError(f"❌ Workflow '{workflow_name}' not found on Galaxy.")
workflow_id = workflows[0]["id"]
print(f"⚙️ Using workflow: {workflow_name} ({workflow_id})")

# ------------------------------
# 5. Define monitor function
# ------------------------------
def monitor_workflow(gi, history_id, sample_name):
    print(f"⏳ Monitoring workflow for sample: {sample_name}")
    while True:
        datasets = gi.histories.show_history(history_id, contents=True)
        states = [d["state"] for d in datasets]
        if all(state in ["ok", "error"] for state in states):
            break
        print(f"  Current states: {states}")
        time.sleep(60)
    print(f"✅ Workflow finished for {sample_name}")

# ------------------------------
# 6. Run workflow for each pair
# ------------------------------
for sample, files in pairs.items():
    if not files["R1"] or not files["R2"]:
        print(f"⚠️ Skipping {sample} — missing R1 or R2")
        continue

    print(f"\n🚀 Processing sample: {sample}")

    # Create new history per sample
    history = gi.histories.create_history(name=f"{sample}_MetaPhlAn")
    print(f"🧬 Created history: {history['name']} ({history['id']})")

    # Upload both files
    print(f"📤 Uploading {files['R1']} and {files['R2']}")
    up_R1 = gi.tools.upload_file(files["R1"], history["id"])
    up_R2 = gi.tools.upload_file(files["R2"], history["id"])

    # Prepare inputs (adjust IDs if your workflow expects different inputs)
    inputs = {
        "0": {"src": "hda", "id": up_R1["outputs"][0]["id"]},
        "1": {"src": "hda", "id": up_R2["outputs"][0]["id"]},
    }

    # Run the workflow
    gi.workflows.get_workflow(workflow_id=workflow_id, history_id=history["id"], inputs=inputs)
    print(f"🧩 Running MetaPhlAn workflow for {sample}...")

    # Monitor until complete
    monitor_workflow(gi, history["id"], sample)

    # Download results
    datasets = gi.histories.show_history(history["id"], contents=True)
    sample_outdir = os.path.join(output_dir, sample)
    os.makedirs(sample_outdir, exist_ok=True)

    for ds in datasets:
        if ds["state"] == "ok":
            safe_name = ds["name"].replace(" ", "_").replace("/", "_")
            output_path = os.path.join(sample_outdir, f"{safe_name}.dat")
            print(f"⬇️ Downloading {ds['name']} → {output_path}")
            gi.datasets.download_dataset(ds["id"], file_path=output_path, use_default_filename=False)

    print(f"📁 Results saved to: {sample_outdir}")

print("\n🎉 All paired samples processed successfully!")
print(f"All results are in: {output_dir}")
