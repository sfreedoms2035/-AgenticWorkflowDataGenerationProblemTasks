import os

skills = {
    "Orchestrator": """---
description: Pipeline orchestrator and main execution framework for GPF tasks.
---

# GPF Pipeline Orchestrator

## Overview
Coordinates the generation, validation, and repair of Generalized Problem Formulations (GPFs) from raw automotive PDF standards. Focuses on extracting implicit engineering knowledge and structuring it into a 17-block JSON schema.

## Run Instruction
- To test the pipeline, execute `python pipeline.py --pdfs Data/test_doc.pdf`
""",
    "GPFProblemFormulator": """---
description: Principal Synthetic Data Engineer handling complex GPF formulation.
---

# GPF Problem Formulator

## Core Identity
PhD Level Problem Formalizer specializing in Autonomous Driving and ADAS.

## Responsibilities
- Translate vague engineering pain points into pure mathematics.
- Write strict objective functions (`argmin(f(x))`) and Python ABC stubs.
- Define hardware constraints, SysML architectures, and rigorous success metrics.
- Produce exactly 1 GPF Output in a 6-Turn compliant QWEN3 format.
""",
    "GPFQualityAssurance": """---
description: Strict validation engine for CoT depth, extraction fidelity, and length bounds.
---

# GPF Quality Assurance

## Mandate
Enforce the bounds and syntax constraints over the Formulator models.

## Specific Checks
1. **Length**: Enforce Answer > 15,000 characters and CoT > 10,000 characters.
2. **Schema**: Verify full parsing of the 10-layer `core_problem_definition` format.
3. **Volume Warning**: Fail generations matching word-salad padding logic or repetition loops.
4. **SysML Definition**: Enforce >100 line XML.
""",
    "GPFValidationRepairer": """---
description: Diagnostics and Remediation Engine.
---

# GPF Validation Repairer

## Process
When `validate_task.py` triggers a FAIL, this engine:
1. Extracts the exact failure codes (e.g., VOLUME FAILURE, IMMERSION FAILURE).
2. Forwards the strict constraints back to Gemini with explicit directives to resolve the deficiency while maintaining original length requirements.
3. Falls back to "Soft Retry" if safety filters reject the problem complexity.
""",
    "GPFDashboardVisualizer": """---
description: Telemetry, generation progress, and GPF JSON metrics visualization.
---

# GPF Dashboard Visualizer

## Reporting
- Summarize task attempt counts and output sizes.
- Report on local repair success vs full generation failure rates.
"""
}

base_dir = r"c:\Users\User\VS_Projects\Helpers\Antigravity\AgenticWorkflowPlaywright_Visuals\.agent\skills"
os.makedirs(base_dir, exist_ok=True)

for skill_name, content in skills.items():
    skill_dir = os.path.join(base_dir, skill_name)
    os.makedirs(skill_dir, exist_ok=True)
    with open(os.path.join(skill_dir, "SKILL.md"), "w", encoding="utf-8") as f:
        f.write(content)

print("SKILLS CREATED SUCCESSFULLY")
