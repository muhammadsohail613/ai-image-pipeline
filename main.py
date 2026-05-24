import os
import sys
import json
import shutil
import time

from processor import remove_background, composite_on_white, check_quality


def load_config(path: str = "config.json") -> dict:
    defaults = {
        "canvas_size": 1000,
        "padding_percent": 0.1,
        "output_format": "JPEG",
        "jpeg_quality": 95,
        "qc_min_foreground": 0.03,
        "qc_max_foreground": 0.97,
        "qc_max_edge_noise": 0.15,
        "input_dir": "input",
        "output_dir": "output",
        "flagged_dir": "flagged",
    }
    if os.path.exists(path):
        with open(path, "r") as f:
            loaded = json.load(f)
        defaults.update(loaded)
        print(f"Config loaded from {path}")
    else:
        print("No config.json found — using defaults")
    return defaults


SUPPORTED_FORMATS = (".jpg", ".jpeg", ".png", ".webp", ".bmp")


def run_batch(config: dict):
    input_dir = config["input_dir"]
    output_dir = config["output_dir"]
    flagged_dir = config["flagged_dir"]

    images = [
        f for f in os.listdir(input_dir)
        if f.lower().endswith(SUPPORTED_FORMATS)
    ]

    if not images:
        print("No images found in input/ folder.")
        return

    print(f"Found {len(images)} image(s) in {input_dir}/\n")

    results = {"success": [], "flagged": [], "error": []}
    start_time = time.time()

    for i, filename in enumerate(images, 1):
        print(f"[{i}/{len(images)}] {filename}")

        input_path = os.path.join(input_dir, filename)
        base_name = os.path.splitext(filename)[0]
        no_bg_path = os.path.join(output_dir, f"{base_name}_no_bg.png")

        r1 = remove_background(input_path, no_bg_path)
        if r1["status"] == "error":
            results["error"].append(filename)
            continue

        qc = check_quality(
            image_path=no_bg_path,
            min_foreground=config["qc_min_foreground"],
            max_foreground=config["qc_max_foreground"],
            max_edge_noise=config["qc_max_edge_noise"],
        )

        if not qc["passed"]:
            flagged_path = os.path.join(flagged_dir, filename)
            shutil.copy(input_path, flagged_path)
            os.remove(no_bg_path)
            print(f"  [FLAGGED] {filename} → {qc['reason']}")
            results["flagged"].append({"file": filename, "reason": qc["reason"]})
            continue

        final_ext = ".jpg" if config["output_format"].upper() == "JPEG" else ".png"
        final_path = os.path.join(output_dir, f"{base_name}_final{final_ext}")

        r2 = composite_on_white(
            input_path=no_bg_path,
            output_path=final_path,
            canvas_size=config["canvas_size"],
            padding_percent=config["padding_percent"],
            output_format=config["output_format"],
        )

        if r2["status"] == "success":
            results["success"].append(filename)
        else:
            results["error"].append(filename)

    elapsed = round(time.time() - start_time, 1)

    print(f"\n--- Batch complete in {elapsed}s ---")
    print(f"  Processed : {len(results['success'])}")
    print(f"  Flagged   : {len(results['flagged'])}")
    print(f"  Errors    : {len(results['error'])}")

    if results["flagged"]:
        print("\n  Flagged files (need manual review):")
        for f in results["flagged"]:
            print(f"    - {f['file']}: {f['reason']}")

    if results["error"]:
        print(f"\n  Failed: {results['error']}")


if __name__ == "__main__":
    config = load_config()
    run_batch(config)