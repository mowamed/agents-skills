---
name: op-banana-pro
description: Generate/edit images with Nano Banana Pro via OpenRouter API. Use for image create/modify requests incl. edits. Supports text-to-image + image-to-image; 1K/2K/4K; use --input-image.
---

# Nano Banana Pro Image Generation & Editing

Generate new images or edit existing ones using Nano Banana Pro (Gemini 3 Pro Image) via the OpenRouter API.

## Usage

Run the script with `uv run` using the path where the skill is installed. Examples below use `$SKILL_DIR` as a placeholder — replace it with the actual path (e.g., `~/.kiro/skills/op-banana-pro`, `.agents/skills/op-banana-pro`, etc.).

**Generate new image:**
```bash
uv run $SKILL_DIR/scripts/generate_image.py --prompt "your image description" --filename "output.png" [--resolution 1K|2K|4K] [--model MODEL] [--output-dir DIR] [--api-key KEY]
```

**Edit existing image:**
```bash
uv run $SKILL_DIR/scripts/generate_image.py --prompt "editing instructions" --filename "output.png" --input-image "path/to/input.png" [--resolution 1K|2K|4K] [--api-key KEY]
```

**Important:** Always run from the user's current working directory so images are saved where the user is working, not in the skill directory.

## CLI Flags

| Flag | Short | Default | Description |
|------|-------|---------|-------------|
| `--prompt` | `-p` | (required) | Image description or editing instructions |
| `--filename` | `-f` | (required) | Output filename (supports `.png`, `.jpg`, `.webp`) |
| `--input-image` | `-i` | — | Input image path for editing |
| `--output-dir` | `-d` | current dir | Directory to save the output image |
| `--resolution` | `-r` | `1K` | Output resolution hint: `1K`, `2K`, or `4K` |
| `--model` | `-m` | `google/gemini-3-pro-image-preview` | OpenRouter model name |
| `--api-key` | `-k` | — | OpenRouter API key (overrides env var) |

## Default Workflow (draft → iterate → final)

Goal: fast iteration without burning time on 4K until the prompt is correct.

- Draft (1K): quick feedback loop
  - `uv run $SKILL_DIR/scripts/generate_image.py --prompt "<draft prompt>" --filename "yyyy-mm-dd-hh-mm-ss-draft.png" --resolution 1K`
- Iterate: adjust prompt in small diffs; keep filename new per run
  - If editing: keep the same `--input-image` for every iteration until you're happy.
- Final (4K): only when prompt is locked
  - `uv run $SKILL_DIR/scripts/generate_image.py --prompt "<final prompt>" --filename "yyyy-mm-dd-hh-mm-ss-final.png" --resolution 4K`

## Resolution Options

**Important limitation:** Unlike the native Gemini SDK, OpenRouter does not expose a dedicated `image_size` parameter. The resolution preference is included as a text hint in the prompt. Output dimensions are not guaranteed — the model uses the hint as guidance.

- **1K** (default) - ~1024px resolution
- **2K** - ~2048px resolution
- **4K** - ~4096px resolution

Map user requests to API parameters:
- No mention of resolution → `1K`
- "low resolution", "1080", "1080p", "1K" → `1K`
- "2K", "2048", "normal", "medium resolution" → `2K`
- "high resolution", "high-res", "hi-res", "4K", "ultra" → `4K`

## Output Formats

The script detects the output format from the filename extension:
- `.png` → PNG (default)
- `.jpg` / `.jpeg` → JPEG (alpha composited onto white background)
- `.webp` → WebP

## API Key

The script checks for API key in this order:
1. `--api-key` argument (use if user provided key in chat)
2. `OPENROUTER_API_KEY` environment variable

If neither is available, the script exits with an error message.

## Preflight + Common Failures (fast fixes)

- Preflight:
  - `command -v uv` (must exist)
  - `test -n "$OPENROUTER_API_KEY"` (or pass `--api-key`)
  - If editing: `test -f "path/to/input.png"`

- Common failures:
  - `Error: No API key provided.` → set `OPENROUTER_API_KEY` or pass `--api-key`
  - `Error loading input image:` → wrong path / unreadable file; verify `--input-image` points to a real image
  - `API error (4xx/5xx):` → wrong key, no access, quota exceeded, or server issue
  - `Request timed out` → transient network issue; the script retries automatically up to 2 times

## Filename Generation

Generate filenames with the pattern: `yyyy-mm-dd-hh-mm-ss-name.png`

**Format:** `{timestamp}-{descriptive-name}.{ext}`
- Timestamp: Current date/time in format `yyyy-mm-dd-hh-mm-ss` (24-hour format)
- Name: Descriptive lowercase text with hyphens
- Extension: `.png`, `.jpg`, or `.webp`
- Keep the descriptive part concise (1-5 words typically)
- Use context from user's prompt or conversation
- If unclear, use random identifier (e.g., `x9k2`, `a7b3`)

Examples:
- Prompt "A serene Japanese garden" → `2026-03-12-14-23-05-japanese-garden.png`
- Prompt "sunset over mountains" → `2026-03-12-15-30-12-sunset-mountains.jpg`
- Unclear context → `2026-03-12-17-12-48-x9k2.png`

## Image Editing

When the user wants to modify an existing image:
1. Check if they provide an image path or reference an image in the current directory
2. Use `--input-image` parameter with the path to the image
3. The prompt should contain editing instructions (e.g., "make the sky more dramatic", "remove the person", "change to cartoon style")
4. Common editing tasks: add/remove elements, change style, adjust colors, blur background, etc.

Note: Large input images are automatically downscaled to max 2048px before sending to the API to reduce latency and payload size. This does not affect the output resolution.

## Prompt Handling

**For generation:** Pass user's image description as-is to `--prompt`. Only rework if clearly insufficient.

**For editing:** Pass editing instructions in `--prompt` (e.g., "add a rainbow in the sky", "make it look like a watercolor painting")

Preserve user's creative intent in both cases.

## Prompt Templates (high hit-rate)

Use templates when the user is vague or when edits must be precise.

- Generation template:
  - "Create an image of: <subject>. Style: <style>. Composition: <camera/shot>. Lighting: <lighting>. Background: <background>. Color palette: <palette>. Avoid: <list>."

- Editing template (preserve everything else):
  - "Change ONLY: <single change>. Keep identical: subject, composition/crop, pose, lighting, color palette, background, text, and overall style. Do not add new objects. If text exists, keep it unchanged."

## Output

- Saves image to current directory (or `--output-dir` if specified)
- Script outputs the full path to the generated image
- **Do not read the image back** - just inform the user of the saved path

## Examples

**Generate new image (PNG):**
```bash
uv run $SKILL_DIR/scripts/generate_image.py --prompt "A serene Japanese garden with cherry blossoms" --filename "2026-03-12-14-23-05-japanese-garden.png" --resolution 4K
```

**Generate as JPEG with output dir:**
```bash
uv run $SKILL_DIR/scripts/generate_image.py --prompt "sunset over mountains" --filename "sunset.jpg" --output-dir ./images --resolution 2K
```

**Edit existing image:**
```bash
uv run $SKILL_DIR/scripts/generate_image.py --prompt "make the sky more dramatic with storm clouds" --filename "2026-03-12-14-25-30-dramatic-sky.png" --input-image "original-photo.jpg"
```

**Use a different model:**
```bash
uv run $SKILL_DIR/scripts/generate_image.py --prompt "a cat in space" --filename "cat.png" --model "google/gemini-2.0-flash-exp:free"
```
