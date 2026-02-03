# Refractor Pipeline

Automated code review and refactoring pipeline using Claude CLI.

## Overview

The pipeline runs multiple Claude CLI sessions sequentially, each performing a specific code review or refactoring task. Each session runs non-interactively with `--dangerously-skip-permissions`.

Before running, creates a local git checkpoint commit for easy rollback.

## Pipeline Phases

### Phase 1: Iterative Roast Loop

```
┌─────────────────────────────────────────────┐
│ 1. Run roast (step 0) with severity         │
│                                             │
│ 2. If non-minor issues exist:               │
│    - Fix each SEVERE/MEDIUM issue           │
│    - Git checkpoint per issue               │
│    - Re-run roast                           │
│                                             │
│ 3. Repeat until only MINOR issues remain    │
└─────────────────────────────────────────────┘
```

#### Severity Classification

| Severity | Description | Action |
|----------|-------------|--------|
| **SEVERE** | Security issues, data loss risks, critical bugs, architectural violations | Fixed automatically |
| **MEDIUM** | Performance issues, code quality problems, missing tests, unclear code, documentation gaps, nice-to-haves | Fixed automatically |
| **MINOR** | Pure style issues (formatting, naming conventions that don't affect readability) | Skipped |

Each roast issue includes:
- **Severity**: SEVERE / MEDIUM / MINOR
- **Affected files**: List of files to modify
- **Description**: What's wrong
- **Suggested fix**: Specific actionable fix instructions

### Phase 2: Project-Wide Steps (1-8)

After the roast loop completes (only MINOR issues remain), the pipeline runs these steps on the **whole project**:

| Step | Name | Description |
|------|------|-------------|
| 1 | Data Architecture Enforcement | Run `/bx_data_architecture_enforcement` |
| 2 | Architecture Review | Review per `python_clean_architecture.md` |
| 3 | LRU Cache Opportunities | Find caching opportunities, precompile regex |
| 4 | Proper Usage of Libraries | Ensure orjson, rtoml, httpx usage |
| 5 | Edge Cases & Security | Review for edge cases, race conditions, security |
| 6 | Test Refractor | Run `/bx_refactor_tests_python` |
| 7 | Code Simplification | Simplify code, remove dead code, modernize |
| 8 | Documentation Review | Verify claude.md, module_reference.md accuracy |

## Usage

```bash
# Run full pipeline (roast loop + project-wide steps)
make refractor

# Run with auto-fix (no prompts, fix all non-minor issues automatically)
make refractor-auto

# Or using the CLI directly
python -m scripts refractor --auto-fix    # Auto-fix mode
python -m scripts refractor --step 0      # Just roast
python -m scripts refractor --step 3      # Just LRU Cache step
```

## Git Checkpoints

The pipeline creates git checkpoints at key points:

1. **Pre-refractor checkpoint**: Before any changes
   - Format: `pre-refractor {version} {timestamp}`

2. **Per-chunk checkpoint**: Before fixing each issue
   - Format: `pre-chunk-{N}: [{SEVERITY}] {title}`

This allows easy rollback if something goes wrong:

```bash
# View checkpoints
git log --oneline

# Rollback to before refractor
git reset --hard HEAD~N
```

## Interactive Prompts

During the roast loop, after displaying issues by severity:

```
Options:
  fix      - Fix all SEVERE and MEDIUM issues, then re-roast
  continue - Skip to project-wide steps (1-8)
  abort    - Cancel the pipeline
```

## Output Files

Roast analysis is saved to timestamped markdown files:
- Location: `$TMPDIR/RISscraper_refractor/roast_{timestamp}.md`

## Standard Fix Suffix

All fix prompts include this suffix:
- Do not create compatibility shims
- Make sure all tests pass
- Update claude.md and module_reference.md
- Update changelog in `[unreleased]` section
