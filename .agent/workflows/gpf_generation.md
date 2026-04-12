---
description: Automatically orchestrates the generation of GPF problem formulation tasks per PDF using Playwright and Gemini Web App.
---

# GPF Generation Workflow

This workflow generates Generalized Problem Formulation (GPF) tasks per PDF by automating the Gemini web interface via `pipeline.py`.

// turbo-all

## EXECUTION STEPS (MANDATORY — Follow in Order)

### Step 1: Load Context
Read the agent configuration to understand paths and current state:
```bash
cat .agent/agent.md
```

### Step 2: Check Current State
Check what PDFs exist and what progress has been made:
```bash
dir Input\*.pdf
type Output\progress.json
```
If `progress.json` doesn't exist, this is a fresh start. If it exists, read it to determine the next PDF / turn / task to process.

### Step 3: Validate Existing Outputs (if any)
Run validation on all existing outputs:
```bash
python pipeline.py --validate-only
```

### Step 4a: Fresh Start — Process All PDFs
```bash
python pipeline.py
```

### Step 4b: Resume After Interruption
```bash
python pipeline.py --resume
```

### Step 4c: Process Limited PDFs (testing)
```bash
python pipeline.py --limit-pdfs 1 --test-setup
```

### Step 5: Post-Pipeline Validation
```bash
python pipeline.py --validate-only
```

### Step 6: Normalize Training Data IDs
```bash
python .agent/scripts/json_aggregator.py
```

### Step 7: Generate Final Dashboard
```bash
python .agent/scripts/generate_dashboard.py
```

---

## WHAT THE PIPELINE DOES AUTOMATICALLY

1. **Classifies** each PDF as Technical or Regulatory
2. **Builds** a full prompt per turn/task/variation with 8-step CoT template + GPF structure
3. **Runs** `run_gemini_playwright_v2.py` (Gemini Pro, zero manual steps)
4. **Extracts** blockwise semantic blocks (`!!!!!BLOCKNAME!!!!!`) → assembles JSON
5. **Validates** output via `validate_task.py` (19 quality gates)
6. **Repairs**: local fix (`auto_repair.py`) → partial (`partial_repair.py`) → Gemini re-prompt
7. **Retries** up to 3 Gemini attempts per task
8. **Saves** progress after every task for resume support

---

## QUALITY GATES

| Gate | Threshold |
|------|-----------|
| CoT length | ≥ 9,000 chars |
| Answer length | ≥ 15,000 chars |
| GPF elements | All 10 present as string blocks |
| Enumerated headers | All sub-element headers present (e.g., "4.1 Symbolic Representation") |
| XML SysML | ≥ 50 lines raw plaintext |
| Python ABC | `class` + `def` present in formal_specification |
| Python Verifier | `def` present in evaluation_verification |
| Math notation | ≥ 5 formal symbols in formal_specification |
| Per-element length | Each element meets minimum char threshold |
| CoT structure | All 31 sub-elements |
| Self-containment | No banned vocabulary |
| Follow-up quality | ≥ 100 chars, no instruction echoes |

## REPAIR STRATEGY

- **Local fixes** (auto_repair.py): JSON parsing, merged content, missing think tags, turn padding
- **Partial repair** (partial_repair.py): Follow-up turn regeneration only
- **Gemini re-prompt**: Volume failures, missing CoT elements, immersion breaks
- **Max 3 Gemini attempts** per task

## AGENT GUIDELINES

- **Always use the scripts.** Never manually edit JSON output files.
- **Always resume, never restart.** Use `--resume` flags. Never delete `progress.json`.
- **Optimize freely.** Modify workflow files, scripts, and skills to improve quality.
