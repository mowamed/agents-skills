# Agents Skills

A collection of reusable skills for AI agents. Each skill is a self-contained module with its own scripts, documentation, and dependencies.

## Repository Structure

```
skills/
  <skill-name>/
    SKILL.md          # Skill metadata, usage docs, and prompt guidance
    scripts/          # Executable scripts for the skill
```

## Available Skills

| Skill | Description |
|-------|-------------|
| [op-banana-pro](skills/op-banana-pro/SKILL.md) | Generate and edit images using Nano Banana Pro (Gemini 3 Pro Image) via OpenRouter API |

## Installation

### Prerequisites

- [uv](https://docs.astral.sh/uv/getting-started/installation/) — Python package runner (scripts declare their own dependencies inline)

### Setup

1. Clone the repository:
   ```bash
   git clone <repo-url> ~/.codex/skills
   ```

2. Set required environment variables for the skills you use. For example, `op-banana-pro` needs:
   ```bash
   export OPENROUTER_API_KEY="your-key-here"
   ```

3. Run any skill script directly with `uv run`:
   ```bash
   uv run ~/.codex/skills/op-banana-pro/scripts/generate_image.py --prompt "a cat in space" --filename "cat.png"
   ```

No `pip install` or virtual environment setup is needed — `uv run` handles dependencies automatically via [inline script metadata](https://docs.astral.sh/uv/guides/scripts/#declaring-script-dependencies).

## Adding a New Skill

1. Create a directory under `skills/` with your skill name
2. Add a `SKILL.md` with frontmatter (`name`, `description`) and usage documentation
3. Place scripts in a `scripts/` subdirectory
4. Use [inline script metadata](https://docs.astral.sh/uv/guides/scripts/#declaring-script-dependencies) in Python scripts so `uv run` resolves dependencies automatically

## License

MIT
