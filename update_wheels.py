import toml
from pathlib import Path

# Path to your blender_manifest.toml
MANIFEST_PATH = Path("blender_manifest.toml")

# Path to the folder containing your downloaded wheels
WHEELS_DIR = Path("wheels")

# Load the existing manifest
manifest = toml.load(MANIFEST_PATH)

# Gather all wheel filenames
wheel_files = ["./wheels/" + f.name for f in WHEELS_DIR.glob("*.whl")]

# Write them into a single "wheels" list
manifest["wheels"] = wheel_files

# Save the updated manifest
with MANIFEST_PATH.open("w") as f:
    toml.dump(manifest, f)

print("blender_manifest.toml updated with wheels =", wheel_files)
