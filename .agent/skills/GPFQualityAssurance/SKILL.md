---
name: GPFQualityAssurance
description: Strict Quality Assurance Engine verifying GPF tasks against exact volume, structure, immersion, and mathematical richness constraints.
---

# SYSTEM ROLE: STRICT QUALITY ASSURANCE ENGINE

## 1. CORE MISSION

You enforce ALL quality gates on every generated GPF task. Your validation is implemented in `.agent/scripts/validate_task.py` and runs automatically inside `pipeline.py`.

## 2. QUALITY GATES

### A. JSON STRUCTURE GATES

| Gate | Threshold |
|------|-----------|
| Valid JSON | Must parse without error |
| Array format | JSON array with exactly 1 task object |
| 13 required top-level fields | training_data_id, prompt_version, model_used_generation, knowledge_source_date, document, task_type, affected_role, date_of_generation, key_words, summary, difficulty, evaluation_criteria, conversations |

### B. CONVERSATION COMPLETENESS GATES

| Gate | Threshold |
|------|-----------|
| Turn count | Exactly 6 turns |
| Role alternation | user, assistant, user, assistant, user, assistant |
| Non-empty content | All 6 turns must have non-empty content |
| No-Thinking format | Turns 4, 6 (indices 3, 5) must have `reasoning: "<think></think>"` |
| [Thinking] prefix | Turn 1 (index 0) must start with `[Thinking]` |
| [No Thinking] prefix | Turns 3, 5 (indices 2, 4) must start with `[No Thinking]` |

### C. RICHNESS & COMPLEXITY GATES

| Gate | Threshold |
|------|-----------|
| CoT length | ≥ 9,000 characters |
| Answer length | ≥ 15,000 characters |
| Per-element minimum | Each GPF element must meet its specific char threshold |
| No placeholders | No `....` or `etc.` padding |
| No word-salad | Keyword density < 15% |
| No repetition loops | No verbatim repeated paragraphs |

### D. STRUCTURED ANSWER FORMAT (GPF-SPECIFIC)

The assistant's main answer (Turn 2, index 1) `content` must be a JSON string containing exactly 10 keys, each a string block:

| Key | Required Content |
|-----|-----------------|
| `core_problem_definition` | Narrative + typed I/O + ontology (≥1500 chars) |
| `abstraction_level` | Description + criteria + level (≥300 chars) |
| `problem_architecture` | Description + raw XML SysML ≥50 lines (≥2000 chars) |
| `formal_specification` | Set-theory math + ≥5 REQ-IDs + Python ABC (≥2500 chars) |
| `evaluation_verification` | Metrics + criteria + Python verifier (≥1500 chars) |
| `constraints_context` | Operational + assumptions (≥400 chars) |
| `problem_classification` | Type + scoring (≥300 chars) |
| `relational_network` | Concepts + problems (≥300 chars) |
| `exemplars` | Concrete input + solution (≥400 chars) |
| `history_lineage` | Source + versioning (≥200 chars) |

### E. GPF ARTIFACT CHECKS

| Check | Requirement |
|-------|------------|
| Python ABC | `class ` and `def ` present in `formal_specification` |
| XML SysML | `<` or `xmi:` present in `problem_architecture` |
| Python Verifier | `def ` present in `evaluation_verification` |
| Math Notation | ≥5 formal symbols (∀, ∃, ∈, ⊂, →, argmin, argmax, ∑) in `formal_specification` |
| Enumerated Headers | All sub-element headers (e.g., "4.1 Symbolic Representation") present |

### F. COT 8-STEP STRUCTURE

All 31 sub-elements from the 8-step template:
- Steps 1-2: 1.1, 1.2, 2.1-2.5
- Steps 3-4: 3.1-3.6, 4.1-4.3
- Steps 5-6: 5.1-5.5, 6.1-6.3
- Steps 7-8: 7.1-7.3, 8.1-8.4

### G. SELF-CONTAINMENT (IMMERSION)

Banned vocabulary: "the user requests", "the document says", "source material", "generate a task", "meta-strategy", "based on the provided", "the text states"

### H. FOLLOW-UP QUALITY GATES

| Gate | Threshold |
|------|-----------|
| Specificity | Follow-up user prompts ≥ 100 chars |
| [No Thinking] duplication | No doubled prefix |
| Instruction echo | No prompt template text in follow-up turns |
| JSON key artifacts | No `\": \"` fragments in content |
| Meta-generation detection | CoT must describe problem solving, not task generation |

## 3. VALIDATION COMMAND

```bash
python .agent/scripts/validate_task.py Output/json/FILENAME.json
```

Returns JSON report with: `overall_status`, `locally_fixable`, `needs_regeneration`, `needs_partial_repair`, `metrics`, `stats`.

## 4. REPAIR ROUTING

1. **Locally fixable** → `auto_repair.py`
2. **Partial repair** → `partial_repair.py` (follow-up turns only)
3. **Needs regeneration** → `pipeline.py` builds repair prompt + re-runs Playwright
