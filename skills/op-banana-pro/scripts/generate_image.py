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
    uv run generate_image.py --prompt "your image description" --filename "output.png" [--resolution 1K|2K|4K] [--api-key KEY]
"""

import argparse
import base64
import json
import os
import sys
from io import BytesIO
from pathlib import Path


def get_api_key(provided_key: str | None) -> str | None:
    if provided_key:
        return provided_key
    return os.environ.get("OPENROUTER_API_KEY")


def encode_image_to_data_url(image_path: str) -> str:
    from PIL import Image as PILImage

    img = PILImage.open(image_path)
    buf = BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"data:image/png;base64,{b64}"


def save_image_from_data_url(data_url: str, output_path: Path):
    from PIL import Image as PILImage

    # Strip "data:image/...;base64," prefix
    header, b64_data = data_url.split(",", 1)
    image_data = base64.b64decode(b64_data)
    image = PILImage.open(BytesIO(image_data))

    if image.mode == 'RGBA':
        rgb = PILImage.new('RGB', image.size, (255, 255, 255))
        rgb.paste(image, mask=image.split()[3])
        rgb.save(str(output_path), 'PNG')
    elif image.mode == 'RGB':
        image.save(str(output_path), 'PNG')
    else:
        image.convert('RGB').save(str(output_path), 'PNG')


def main():
    parser = argparse.ArgumentParser(
        description="Generate images using Nano Banana Pro (Gemini 3 Pro Image) via OpenRouter"
    )
    parser.add_argument("--prompt", "-p", required=True, help="Image description/prompt")
    parser.add_argument("--filename", "-f", required=True, help="Output filename (e.g., sunset-mountains.png)")
    parser.add_argument("--input-image", "-i", help="Optional input image path for editing/modification")
    parser.add_argument("--resolution", "-r", choices=["1K", "2K", "4K"], default="1K", help="Output resolution: 1K (default), 2K, or 4K")
    parser.add_argument("--api-key", "-k", help="OpenRouter API key (overrides OPENROUTER_API_KEY env var)")

    args = parser.parse_args()

    api_key = get_api_key(args.api_key)
    if not api_key:
        print("Error: No API key provided.", file=sys.stderr)
        print("Please either:", file=sys.stderr)
        print("  1. Provide --api-key argument", file=sys.stderr)
        print("  2. Set OPENROUTER_API_KEY environment variable", file=sys.stderr)
        sys.exit(1)

    import requests

    output_path = Path(args.filename)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Build message content
    output_resolution = args.resolution
    content = []

    if args.input_image:
        try:
            from PIL import Image as PILImage
            img = PILImage.open(args.input_image)
            width, height = img.size
            img.close()

            if args.resolution == "1K":
                max_dim = max(width, height)
                if max_dim >= 3000:
                    output_resolution = "4K"
                elif max_dim >= 1500:
                    output_resolution = "2K"
                print(f"Auto-detected resolution: {output_resolution} (from input {width}x{height})")

            data_url = encode_image_to_data_url(args.input_image)
            content.append({"type": "image_url", "image_url": {"url": data_url}})
            print(f"Loaded input image: {args.input_image}")
            print(f"Editing image with resolution {output_resolution}...")
        except Exception as e:
            print(f"Error loading input image: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"Generating image with resolution {output_resolution}...")

    # Append resolution hint + prompt
    prompt_text = f"[Output resolution: {output_resolution}] {args.prompt}"
    content.append({"type": "text", "text": prompt_text})

    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "model": "google/gemini-3-pro-image-preview",
                "messages": [{"role": "user", "content": content}],
                "modalities": ["image", "text"],
            }),
        )

        result = response.json()

        if result.get("error"):
            print(f"API error: {result['error']}", file=sys.stderr)
            sys.exit(1)

        image_saved = False
        if result.get("choices"):
            message = result["choices"][0]["message"]

            # Print any text response
            if message.get("content"):
                print(f"Model response: {message['content']}")

            # Save generated image
            if message.get("images"):
                data_url = message["images"][0]["image_url"]["url"]
                save_image_from_data_url(data_url, output_path)
                image_saved = True

        if image_saved:
            print(f"\nImage saved: {output_path.resolve()}")
        else:
            print("Error: No image was generated in the response.", file=sys.stderr)
            sys.exit(1)

    except Exception as e:
        print(f"Error generating image: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
