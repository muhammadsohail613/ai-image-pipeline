# ✦ PixelDrop — AI Product Image Pipeline
<img width="1680" height="1050" alt="Screenshot 2026-05-24 at 9 07 35 PM" src="https://github.com/user-attachments/assets/13dff421-c1aa-43d7-b880-1765cd54859a" />

> Automated background removal and white-canvas generation for Amazon, Shopify, and e-commerce product catalogs.

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.44-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![rembg](https://img.shields.io/badge/rembg-u2net-6B9E9A?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-F2B84B?style=flat-square)
![Platform](https://img.shields.io/badge/Platform-macOS%20M2%20%7C%20Linux-E87B72?style=flat-square)

---

## What it does

PixelDrop takes raw product photos and outputs clean, marketplace-ready images automatically — no Photoshop, no manual editing, no per-image fees.

| Input | Output |
|-------|--------|
| Product on any background | Product on pure white 1000×1000px canvas |
| Street photo, lifestyle shot, studio photo | Amazon/Shopify spec-compliant JPEG or PNG |
| Single image or folder of hundreds | Batch processed with quality report |

**Processing time:** ~2–3 seconds per image on Apple M2.

---

## Features

- **AI background removal** using the u2net model via `rembg` with alpha matting for clean edges
- **White canvas compositing** — auto-centered, configurable padding, custom output dimensions
- **Batch processing** — process an entire product catalog in one run
- **Quality check engine** — automatically flags low-confidence masks (foreground ratio, edge noise detection) into a separate `flagged/` folder for manual review
- **Streamlit UI** — drag-and-drop interface with live before/after preview and ZIP download
- **Config-driven** — all settings controlled via `config.json`, no code changes needed
- **M2 optimized** — ARM64 `onnxruntime` build, runs fully on Apple Silicon

---

## Project structure

```
ai-image-pipeline/
│
├── app.py              # Streamlit web UI
├── processor.py        # Core AI functions (remove_background, composite_on_white, check_quality)
├── main.py             # CLI batch runner
├── config.json         # Pipeline settings
├── requirements.txt    # Dependencies
│
├── input/              # Drop product images here
├── output/             # Processed images saved here
└── flagged/            # Low-confidence images moved here for review
```

---

## Quickstart

### 1. Clone the repo

```bash
git clone https://github.com/muhammadsohail613/ai-image-pipeline.git
cd ai-image-pipeline
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

> **Apple Silicon (M2/M3):** The ARM64 build of `onnxruntime` will be installed automatically. No extra steps needed.

### 4. Run the Streamlit app

```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

### 5. Or run batch processing from the CLI

Drop images into the `input/` folder, then:

```bash
python main.py
```

Processed images appear in `output/`. Flagged images appear in `flagged/`.

---

## Configuration

Edit `config.json` to change pipeline behaviour without touching code:

```json
{
  "canvas_size": 1000,
  "padding_percent": 0.1,
  "output_format": "JPEG",
  "jpeg_quality": 95,
  "qc_min_foreground": 0.03,
  "qc_max_foreground": 0.97,
  "qc_max_edge_noise": 0.15,
  "input_dir": "input",
  "output_dir": "output",
  "flagged_dir": "flagged"
}
```

| Setting | Description |
|---------|-------------|
| `canvas_size` | Output image dimensions in pixels (square). Amazon standard: 1000 |
| `padding_percent` | Empty space around the product as a fraction of canvas size |
| `output_format` | `"JPEG"` for smaller files, `"PNG"` for transparency |
| `jpeg_quality` | JPEG compression quality (1–95). 95 = near lossless |
| `qc_min_foreground` | Flag images where foreground is less than this % of canvas |
| `qc_max_foreground` | Flag images where background may not be fully removed |
| `qc_max_edge_noise` | Flag images with rough or noisy edges above this threshold |

---

## How the quality check works

After background removal, each image is analyzed before compositing:

1. **Foreground ratio** — calculates what percentage of pixels are foreground. Too small = product not detected. Too large = background not removed.
2. **Edge noise ratio** — measures semi-transparent pixels along the mask edge. High noise = rough cutout (common with glass, hair, or transparent products).
3. **Decision** — clean images go to `output/`, flagged images go to `flagged/` with the reason logged.

The flagging thresholds are tunable in `config.json` without touching code.

---

## Tech stack

| Component | Library |
|-----------|---------|
| Background removal | `rembg` + u2net model |
| Edge refinement | `pymatting` alpha matting |
| Image processing | `Pillow`, `OpenCV`, `NumPy` |
| ML inference | `onnxruntime` (ARM64 on M2) |
| Web UI | `Streamlit` |
| Model download | `pooch` (cached after first run) |

---

## Use cases

- **E-commerce sellers** — bulk-process Amazon/Shopify product catalogs
- **Agencies** — automate image prep for multiple brand clients
- **Dropshippers** — clean supplier images before listing
- **Photographers** — batch white-canvas output for product shoots

---

## Upwork portfolio

This project is part of my AI engineering portfolio on Upwork.

- **Profile:** [upwork.com/freelancers/~sohail](https://www.upwork.com/freelancers/)
- **Specializations:** Python, Computer Vision, AI Automation, Streamlit, RAG pipelines
- **Top Rated** — 50+ projects, 100% Job Success Score

---

## Author

**Muhammad Sohail**
BS Artificial Intelligence — Air University Islamabad
GitHub: [@muhammadsohail613](https://github.com/muhammadsohail613)

---

## License

MIT License — free to use, modify, and distribute with attribution.
