---
name: Orchestrator
description: Pipeline orchestrator and main execution framework for GPF problem formulation tasks.
---

# GPF Pipeline Orchestrator

## Overview
Coordinates the generation, validation, and repair of Generalized Problem Formulations (GPFs) from raw automotive PDF standards. Converts implicit engineering knowledge into rigorous mathematical problem specifications structured as a 10-element blockwise JSON schema.

## Run Instructions
```bash
python pipeline.py                              # Process all PDFs
python pipeline.py --limit-pdfs 1 --test-setup  # Test with 1 PDF
python pipeline.py --resume                     # Resume from checkpoint
python pipeline.py --validate-only              # Validate existing outputs
```

## Pipeline Flow
1. Classify PDF (Technical vs Regulatory)
2. Build prompt per turn/task/variation
3. Run Gemini via Playwright (`run_gemini_playwright_v2.py`)
4. Extract blockwise semantic blocks → assemble JSON
5. Validate via `validate_task.py` (19 quality gates)
6. Repair: local (`auto_repair.py`) → partial (`partial_repair.py`) → Gemini re-prompt
7. Max 3 attempts per task. Save progress after each.
