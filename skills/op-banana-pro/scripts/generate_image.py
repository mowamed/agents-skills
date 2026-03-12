#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "requests>=2.28.0",
#     "pillow>=10.0.0",
# ]
# ///
"""
Generate images using Nano Banana Pro (Gemini 3 Pro Image) via OpenRouter API.

Usage:
    uv run generate_image.py --prompt "description" --filename "output.png" [options]
"""

import argparse
import base64
import json
import os
import sys
import time
from io import BytesIO
from pathlib import Path

DEFAULT_MODEL = "google/gemini-3-pro-image-preview"
MAX_INPUT_DIM = 2048
MAX_RETRIES = 2
TIMEOUT = 120


def get_api_key(provided_key: str | None) -> str | None:
    return provided_key or os.environ.get("OPENROUTER_API_KEY")


def downscale_image(img):
    """Downscale image so max dimension is MAX_INPUT_DIM."""
    from PIL import Image as PILImage
    w, h = img.size
    if max(w, h) <= MAX_INPUT_DIM:
        return img
    ratio = MAX_INPUT_DIM / max(w, h)
    new_size = (int(w * ratio), int(h * ratio))
    return img.resize(new_size, PILImage.LANCZOS)


def encode_image_to_data_url(image_path: str) -> tuple[str, tuple[int, int]]:
    from PIL import Image as PILImage
    img = PILImage.open(image_path)
    original_size = img.size
    img = downscale_image(img)
    buf = BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"data:image/png;base64,{b64}", original_size


def save_image(data_url: str, output_path: Path):
    from PIL import Image as PILImage
    _, b64_data = data_url.split(",", 1)
    image = PILImage.open(BytesIO(base64.b64decode(b64_data)))

    ext = output_path.suffix.lower()
    if ext in (".jpg", ".jpeg"):
        fmt, mode = "JPEG", "RGB"
    elif ext == ".webp":
        fmt, mode = "WEBP", "RGBA"
    else:
        fmt, mode = "PNG", None

    if mode and image.mode != mode:
        if image.mode == "RGBA" and mode == "RGB":
            bg = PILImage.new("RGB", image.size, (255, 255, 255))
            bg.paste(image, mask=image.split()[3])
            image = bg
        else:
            image = image.convert(mode)

    image.save(str(output_path), fmt)


def api_request(url: str, headers: dict, payload: dict) -> dict:
    import requests
    for attempt in range(MAX_RETRIES + 1):
        try:
            resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=TIMEOUT)
        except requests.Timeout:
            if attempt < MAX_RETRIES:
                print(f"Request timed out, retrying ({attempt + 1}/{MAX_RETRIES})...")
                time.sleep(2 ** attempt)
                continue
            print("Error: Request timed out after all retries.", file=sys.stderr)
            sys.exit(1)

        if resp.status_code >= 500 and attempt < MAX_RETRIES:
            print(f"Server error {resp.status_code}, retrying ({attempt + 1}/{MAX_RETRIES})...")
            time.sleep(2 ** attempt)
            continue

        if resp.status_code != 200:
            try:
                err = resp.json()
            except Exception:
                err = resp.text
            print(f"API error ({resp.status_code}): {err}", file=sys.stderr)
            sys.exit(1)

        try:
            return resp.json()
        except Exception:
            print(f"Error: Non-JSON response from API:\n{resp.text[:500]}", file=sys.stderr)
            sys.exit(1)

    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Generate images via OpenRouter")
    parser.add_argument("--prompt", "-p", required=True)
    parser.add_argument("--filename", "-f", required=True)
    parser.add_argument("--input-image", "-i", help="Input image for editing")
    parser.add_argument("--output-dir", "-d", help="Output directory (default: current dir)")
    parser.add_argument("--resolution", "-r", choices=["1K", "2K", "4K"], default="1K")
    parser.add_argument("--model", "-m", default=DEFAULT_MODEL, help=f"Model name (default: {DEFAULT_MODEL})")
    parser.add_argument("--api-key", "-k", help="OpenRouter API key")
    args = parser.parse_args()

    api_key = get_api_key(args.api_key)
    if not api_key:
        print("Error: No API key provided.", file=sys.stderr)
        print("Set OPENROUTER_API_KEY or pass --api-key.", file=sys.stderr)
        sys.exit(1)

    output_path = Path(args.output_dir) / args.filename if args.output_dir else Path(args.filename)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    resolution = args.resolution
    content = []

    if args.input_image:
        try:
            data_url, (orig_w, orig_h) = encode_image_to_data_url(args.input_image)
            content.append({"type": "image_url", "image_url": {"url": data_url}})

            if args.resolution == "1K":
                max_dim = max(orig_w, orig_h)
                if max_dim >= 3000:
                    resolution = "4K"
                elif max_dim >= 1500:
                    resolution = "2K"

            print(f"Loaded input image: {args.input_image} ({orig_w}x{orig_h})")
            print(f"Editing with resolution {resolution}...")
        except Exception as e:
            print(f"Error loading input image: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"Generating image with resolution {resolution}...")

    content.append({"type": "text", "text": f"[Output resolution: {resolution}] {args.prompt}"})

    result = api_request(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        payload={
            "model": args.model,
            "messages": [{"role": "user", "content": content}],
            "modalities": ["image", "text"],
        },
    )

    if result.get("error"):
        print(f"API error: {result['error']}", file=sys.stderr)
        sys.exit(1)

    image_saved = False
    if result.get("choices"):
        message = result["choices"][0]["message"]
        if message.get("content"):
            print(f"Model response: {message['content']}")
        if message.get("images"):
            save_image(message["images"][0]["image_url"]["url"], output_path)
            image_saved = True

    if image_saved:
        print(f"\nImage saved: {output_path.resolve()}")
    else:
        print("Error: No image was generated in the response.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
