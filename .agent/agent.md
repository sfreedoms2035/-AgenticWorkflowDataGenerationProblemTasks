# Agent Configuration

## Environment
- **OS:** Windows 11
- **Python:** Conda (base)
- **Browser Automation:** Playwright (persistent profile in `.playwright_profile/`)

## Project Paths
- **Project Root:** `C:\Users\User\VS_Projects\Helpers\Antigravity\AgenticWorkflowPlaywright_Visuals`
- **Input PDFs:** `Input/` (relative to project root)
- **Output JSON:** `Output/json/`
- **Output Thinking:** `Output/thinking/`
- **QA & Eval:** `Eval/`
- **Scripts:** `.agent/scripts/`
- **Prompts:** `.agent/prompts/`

## Core Pipeline Entry Point
```
python pipeline.py                              # Process all PDFs
python pipeline.py --limit-pdfs 1 --test-setup  # Test with 1 PDF
python pipeline.py --resume                     # Resume from checkpoint
python pipeline.py --validate-only              # Validate existing outputs
```

## Scripts (`.agent/scripts/`)
| Script | Purpose |
|--------|---------|
| `validate_task.py` | Full quality gate validation (19 gates: JSON, structure, richness, GPF elements, CoT, immersion) |
| `auto_repair.py` | Local repair engine (merged content, turn padding, think tags, metadata synthesis) |
| `partial_repair.py` | Follow-up turn regeneration via focused Gemini prompt |
| `json_aggregator.py` | Post-processing: normalize training_data_id fields |
| `generate_dashboard.py` | Generate HTML dashboard with pipeline stats |

## Playwright Automation (`run_gemini_playwright_v2.py`)
| Feature | Detail |
|---------|--------|
| Model Selection | Always selects Gemini Pro automatically |
| Extraction | Blockwise semantic blocks (`!!!!!BLOCKNAME!!!!!`) → JSON assembly |
| Canvas Defense | DOM detection + escape + prompt-level prevention |
| Exit Codes | 0 = valid JSON saved, 1 = failure |

## Retry Logic
- **Max 3 Gemini attempts** per task
- Between each attempt: local repair → partial repair → Gemini re-prompt
- Dashboard generates after completed PDFs

## Quality Gates (validate_task.py)
| Gate | Threshold |
|------|-----------|
| CoT length | ≥ 9,000 chars |
| Answer length | ≥ 15,000 chars |
| GPF elements | All 10 string blocks present |
| Enumerated headers | All sub-element headers (e.g., "4.1 Symbolic Representation") |
| XML SysML | ≥ 50 lines raw plaintext |
| Python ABC | `class` + `def` in formal_specification |
| Python Verifier | `def` in evaluation_verification |
| Math notation | ≥ 5 formal symbols |
| Per-element min length | Each element meets char threshold |
| CoT structure | All 31 sub-elements |
| Self-containment | No banned vocabulary |
| Follow-up quality | ≥ 100 chars, specificity required |

## File Naming Convention
```
{DocShort}_Turn{N}_Task{K}.json        # Output JSON
{DocShort}_Turn{N}_Task{K}.txt         # Thinking trace
{DocShort}_Turn{N}_Task{K}_Prompt.txt  # Generation prompt
{DocShort}_Turn{N}_Task{K}_QA.json     # QA validation report
```
