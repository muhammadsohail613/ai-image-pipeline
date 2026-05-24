import os
import sys
import io

os.environ["OMP_MAX_ACTIVE_LEVELS"] = "2"

from rembg import remove, new_session
from PIL import Image

session = new_session("u2net")


def remove_background(input_path: str, output_path: str) -> dict:
    result = {
        "input": input_path,
        "output": output_path,
        "status": None,
        "error": None,
        "input_size_kb": 0,
        "output_size_kb": 0,
    }

    try:
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")

        supported = (".jpg", ".jpeg", ".png", ".webp", ".bmp")
        if not input_path.lower().endswith(supported):
            raise ValueError(f"Unsupported format. Use: {supported}")

        result["input_size_kb"] = round(os.path.getsize(input_path) / 1024, 1)

        img = Image.open(input_path).convert("RGBA")

        old_stderr = sys.stderr
        sys.stderr = io.StringIO()
        try:
            output = remove(
                img,
                session=session,
                alpha_matting=True,
                alpha_matting_foreground_threshold=240,
                alpha_matting_background_threshold=10,
                alpha_matting_erode_size=10,
            )
        finally:
            sys.stderr = old_stderr

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        output.save(output_path, "PNG")

        result["output_size_kb"] = round(os.path.getsize(output_path) / 1024, 1)
        result["status"] = "success"
        print(f"  [OK] {os.path.basename(input_path)} → {result['output_size_kb']} KB")

    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        print(f"  [ERROR] {os.path.basename(input_path)}: {e}")

    return result


def composite_on_white(
    input_path: str,
    output_path: str,
    canvas_size: int = 1000,
    padding_percent: float = 0.1,
    output_format: str = "JPEG",
) -> dict:
    result = {
        "input": input_path,
        "output": output_path,
        "status": None,
        "error": None,
        "canvas_size": canvas_size,
        "output_size_kb": 0,
    }

    try:
        img = Image.open(input_path).convert("RGBA")
        canvas = Image.new("RGBA", (canvas_size, canvas_size), (255, 255, 255, 255))

        padding = int(canvas_size * padding_percent)
        max_product_size = canvas_size - (2 * padding)
        img.thumbnail((max_product_size, max_product_size), Image.LANCZOS)

        paste_x = (canvas_size - img.width) // 2
        paste_y = (canvas_size - img.height) // 2
        canvas.paste(img, (paste_x, paste_y), mask=img)

        os.makedirs(
            os.path.dirname(output_path) if os.path.dirname(output_path) else ".",
            exist_ok=True
        )

        if output_format.upper() == "JPEG":
            final = canvas.convert("RGB")
            final.save(output_path, "JPEG", quality=95)
        else:
            canvas.save(output_path, "PNG")

        result["output_size_kb"] = round(os.path.getsize(output_path) / 1024, 1)
        result["status"] = "success"
        print(f"  [OK] Composited → {output_path} ({result['output_size_kb']} KB)")

    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        print(f"  [ERROR] Composite failed: {e}")

    return result


def check_quality(
    image_path: str,
    min_foreground: float = 0.03,
    max_foreground: float = 0.97,
    max_edge_noise: float = 0.15,
) -> dict:
    import numpy as np

    result = {"passed": True, "reason": None}

    try:
        img = Image.open(image_path).convert("RGBA")
        arr = np.array(img)
        alpha = arr[:, :, 3]
        total_pixels = alpha.size

        foreground_pixels = int(np.sum(alpha > 10))
        foreground_ratio = foreground_pixels / total_pixels

        if foreground_ratio < min_foreground:
            result["passed"] = False
            result["reason"] = f"foreground too small ({foreground_ratio:.1%})"
            return result

        if foreground_ratio > max_foreground:
            result["passed"] = False
            result["reason"] = f"background may not be removed ({foreground_ratio:.1%})"
            return result

        edge_mask = (alpha > 5) & (alpha < 250)
        edge_noise_ratio = int(np.sum(edge_mask)) / total_pixels

        if edge_noise_ratio > max_edge_noise:
            result["passed"] = False
            result["reason"] = f"noisy edges ({edge_noise_ratio:.1%} semi-transparent pixels)"
            return result

    except Exception as e:
        result["passed"] = False
        result["reason"] = f"could not analyze: {e}"

    return result


if __name__ == "__main__":
    print("--- Step 1: Remove background ---")
    r1 = remove_background("input/test.jpg", "output/test_no_bg.png")

    print("\n--- Step 2: Composite on white canvas ---")
    r2 = composite_on_white(
        input_path="output/test_no_bg.png",
        output_path="output/test_final.jpg",
        canvas_size=1000,
        padding_percent=0.1,
        output_format="JPEG",
    )

    print("\nBackground removal:", r1["status"])
    print("White canvas:", r2["status"])