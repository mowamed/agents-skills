# Agents Skills

A collection of reusable skills for AI agents. Each skill is a self-contained module with its own scripts, documentation, and dependencies.

Skills follow the open [Agent Skills](https://agentskills.io) standard — a `SKILL.md` file with YAML frontmatter that any compatible AI agent can discover and activate.

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

## Prerequisites

- [uv](https://docs.astral.sh/uv/getting-started/installation/) — Python package runner (scripts declare their own dependencies inline)

## Installing a Skill

### Option A: Using the `skills` CLI (recommended)

The [skills CLI](https://github.com/vercel-labs/skills) is a package manager that installs skills for 40+ AI agents. It auto-detects which agents you have installed and handles symlinks/copies for each one.

```bash
# Interactive — detects your agents and lets you pick skills
npx skills install <repo-url>

# Install a specific skill for a specific agent
npx skills install <repo-url> --skill op-banana-pro --agent <agent-name>

# Install globally (available across all projects)
npx skills install <repo-url> --skill op-banana-pro --agent <agent-name> -g
```

### Option B: Manual installation per agent

Clone the repo, then symlink or copy the skill folder into the location your agent expects.

```bash
git clone <repo-url> /tmp/agents-skills
```

Then follow the instructions for your agent below.

---

#### Kiro (IDE & CLI)

Kiro reads skills from `.kiro/skills/` (project) or `~/.kiro/skills/` (global).

```bash
# Project-scoped
mkdir -p .kiro/skills
ln -s /tmp/agents-skills/skills/op-banana-pro .kiro/skills/op-banana-pro

# Global
mkdir -p ~/.kiro/skills
ln -s /tmp/agents-skills/skills/op-banana-pro ~/.kiro/skills/op-banana-pro
```

Skills activate automatically when your request matches the skill's description.

---

#### Claude Code

Claude Code reads skills from `.claude/skills/` (project) or `~/.claude/skills/` (global).

```bash
# Project-scoped
mkdir -p .claude/skills
ln -s /tmp/agents-skills/skills/op-banana-pro .claude/skills/op-banana-pro

# Global
mkdir -p ~/.claude/skills
ln -s /tmp/agents-skills/skills/op-banana-pro ~/.claude/skills/op-banana-pro
```

---

#### Codex (OpenAI)

Codex is a universal agent — it reads from `.agents/skills/` (project) or `~/.config/agents/skills/` (global).

```bash
# Project-scoped
mkdir -p .agents/skills
ln -s /tmp/agents-skills/skills/op-banana-pro .agents/skills/op-banana-pro

# Global
mkdir -p ~/.config/agents/skills
ln -s /tmp/agents-skills/skills/op-banana-pro ~/.config/agents/skills/op-banana-pro
```

---

#### OpenCode

OpenCode is also a universal agent — same paths as Codex.

```bash
mkdir -p .agents/skills
ln -s /tmp/agents-skills/skills/op-banana-pro .agents/skills/op-banana-pro
```

---

#### Cursor

Cursor reads skills from `.cursor/skills/`.

```bash
mkdir -p .cursor/skills
ln -s /tmp/agents-skills/skills/op-banana-pro .cursor/skills/op-banana-pro
```

---

#### GitHub Copilot

Copilot is a universal agent — reads from `.agents/skills/`.

```bash
mkdir -p .agents/skills
ln -s /tmp/agents-skills/skills/op-banana-pro .agents/skills/op-banana-pro
```

---

#### Cline

Cline reads skills from `.cline/skills/`.

```bash
mkdir -p .cline/skills
ln -s /tmp/agents-skills/skills/op-banana-pro .cline/skills/op-banana-pro
```

---

#### Windsurf

```bash
mkdir -p .windsurf/skills
ln -s /tmp/agents-skills/skills/op-banana-pro .windsurf/skills/op-banana-pro
```

---

#### Gemini CLI

Gemini CLI is a universal agent — reads from `.agents/skills/`.

```bash
mkdir -p .agents/skills
ln -s /tmp/agents-skills/skills/op-banana-pro .agents/skills/op-banana-pro
```

---

### Environment Variables

After installing, set the required env vars for the skills you use. For example, `op-banana-pro` needs:

```bash
export OPENROUTER_API_KEY="your-key-here"
```

### Running Scripts

No `pip install` or virtual environment needed — `uv run` handles dependencies automatically via [inline script metadata](https://docs.astral.sh/uv/guides/scripts/#declaring-script-dependencies):

```bash
uv run /path/to/agents-skills/skills/op-banana-pro/scripts/generate_image.py --prompt "a cat in space" --filename "cat.png"
```

## Adding a New Skill

1. Create a directory under `skills/` with your skill name
2. Add a `SKILL.md` with frontmatter (`name`, `description`) and usage documentation
3. Place scripts in a `scripts/` subdirectory
4. Use [inline script metadata](https://docs.astral.sh/uv/guides/scripts/#declaring-script-dependencies) in Python scripts so `uv run` resolves dependencies automatically

## License

MIT
