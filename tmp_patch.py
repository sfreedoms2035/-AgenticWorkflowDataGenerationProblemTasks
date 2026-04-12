import re
import os

with open("c:\\Users\\User\\VS_Projects\\Helpers\\Antigravity\\AgenticWorkflowPlaywright_Visuals\\pipeline.py", "r", encoding="utf-8") as f:
    content = f.read()

# Replace MAX_GEMINI_ATTEMPTS if it needs to be 3 (it already is 3, but I'll make sure it's set as expected)
content = re.sub(r'MAX_GEMINI_ATTEMPTS\s*=\s*\d+', 'MAX_GEMINI_ATTEMPTS = 3', content)

new_prompt_func = '''def build_generation_prompt(variation, turn, task_idx, doc_name, mode, is_soft_retry=False):
    """Build the full generation prompt per turn/task/variation."""
    diff, strategy, role = variation
    from datetime import datetime
    date_str = datetime.now().strftime('%Y-%m-%d')
    date_compact = datetime.now().strftime('%Y%m%d')
    
    # We call get_doc_short_name locally as it's defined in pipeline.py
    doc_short = get_doc_short_name(doc_name)

    prompt = f"""<instructions>
# SYSTEM ROLE: PhD Level Problem Formalizer (GPF DOMAIN)

## 1. CORE MISSION
Generate exactly 1 distinct Generalized Problem Formulation (GPF) Task (Outputting as a single element for this turn, but contextually aware of the pipeline). You will convert the document's implicit engineering pain points into rigorous, machine-interpretable formal mathematical problems. You do not solve problems; you formalize them.

<variation>
- Difficulty: {diff}/100
- Meta-Strategy: {strategy}
- Assigned Role: {role}
- Document Classification: {mode}
</variation>

## 2. CRITICAL QUALITY GATES & VOLUME FORCING MANDATE
*   **Reasoning (CoT) Minimum 10k Chars:** Act as a Concept Engineer actively wrestling with how to translate vague engineering pain-points into pure mathematics. Explicitly draft mapping tables between real-world physics and mathematical sets inside the CoT. If the key word [No Thinking] is set, keep the content empty between the think tags.
*   **Answer Length (>15k Chars):** You must write at a PhD level.
    *   The `formal_specification` MUST include pure mathematical set-theory formalisms, strict objective functions (e.g., `argmin(f(x))`), AND a massive Python abstract base class (ABC) stub acting as the programmatic interface.
    *   The `problem_architecture` MUST include 100+ lines of raw XML SysML definitions.
    *   The `evaluation_verification` MUST include complete, runnable Python script logic capable of benchmarking the problem.
*   **Absolute Self-Containment:** Do not reference the original text. The GPF must stand alone as an industry-standard problem definition.

## 3. ABSOLUTE IN-UNIVERSE IMMERSION MANDATE (ANTI-META RULE)
You are simulating a real-world engineering interaction. You MUST NOT "break the fourth wall." You are strictly forbidden from writing meta-commentary about task generation, character limits, meta-strategies, or extracting data from documents. 

**RULE 1: THE SIMULATED USER (No Meta-Prompts)**
The `content` for `role: "user"` must be written entirely in-character as an engineer or manager facing a real crisis or architectural need. It must NEVER sound like a prompt engineer commanding an AI.
* ❌ **BAD (Meta):** "[Thinking] As the Forensics Lead, write a massive 3-paragraph problem statement demanding a >400 line Rust code implementation based on the document's Meta-Strategy."
* ✅ **GOOD (In-Universe):** "[Thinking] We have a critical blocker. During yesterday's simulation, our crash-logging timestamps were corrupted upon power loss. I need you to architect a highly optimized, lock-free, cryptographically hashed ring-buffer in Rust to solve this liability issue. The strict constraints are..."

**RULE 2: THE INTERNAL MONOLOGUE (No Task Generation Thoughts)**
Your `<think>` block is the internal brain of the Expert Engineer actively solving the problem. It is NOT the brain of an AI generating a dataset. NEVER mention the user's prompt structure, the source document, or the goal of generating tasks. 
* ❌ **BAD (Meta):** "<think> 1.1 Deconstruct the Prompt: The user wants me to generate a Rust logging mechanism. I need to make sure I write 10,000 characters and use the document. Let me start drafting the 5-Whys table... </think>"
* ✅ **GOOD (In-Universe):** "<think> 1.1 Deconstruct the Request: The Forensics Lead needs an immutable ring-buffer in Rust. The memory constraints on this ECU are incredibly tight, meaning I cannot use standard heap allocation. I must evaluate atomic memory orderings and calculate the payload sizes for the cryptographic hashes... </think>"

**RULE 3: THE FOLLOW-UP QUESTIONS (Natural Dialogue)**
The follow-up questions from the user must be natural, organic engineering questions.
* ❌ **BAD (Meta):** "[No Thinking] Write a follow up question inquiring about how the objective function constraints handle outliers."
* ✅ **GOOD (In-Universe):** "[No Thinking] Looking at the objective function you just wrote, how exactly does the matrix math prevent an overflow if we get a sudden burst of stochastic sensor outliers?"

**RULE 4: BANNED VOCABULARY**
Never use the words "prompt", "generate", "the user requests", "this task", "meta-strategy", "the document", "the text", or "source material" in the generated JSON output. Treat the concepts as your own lived engineering reality.

## 4. STRICT JSON SYNTAX & TEMPLATE LOCK
*(Double escape all \\" and \\\\n. Copy-paste the exact 8-Step CoT Template into your `<think>` block).*
Do NOT use Canvas, Gems, side-panels, or any interactive coding interface. ALL output must be raw text.

## 5. THE 8-STEP MONOLOGUE TEMPLATE
You MUST literally copy, paste, and fully populate this exact 8-step template inside your Turn 1 `<think>` block. Do not skip any numbering.

<think>
1. Initial Query Analysis & Scoping
1.1. Deconstruct the Prompt: Write a highly detailed analysis of the core physical/computational engineering problem, implicit intent, and strict constraints.
1.2. Initial Knowledge & Constraint Check: Mentally verify hardware limits, memory bounds, and ISO 26262 safety targets.
2. Assumptions & Context Setting
2.1. Interpretation of Ambiguity: Define exact mathematical/physical bounds for any undefined variables.
2.2. Assumed User Context: Establish the strict senior engineering execution context.
2.3. Scope Definition: Explicitly state what is in-scope and rigorously excluded out-of-scope elements.
2.4. Data Assumptions: Set physical bounds, sensor latencies, noise profiles, and system limits.
2.5. Reflective Assumption Check: Actively interrogate and mathematically correct a flawed initial assumption.
3. High-Level Plan Formulation
3.1. Explore Solution Scenarios: Draft multiple high-level architectural approaches.
3.2. Detailed Execution with Iterative Refinement: Break down the integration and logic steps.
3.3. Self-Critique and Correction: Pause and critique the initial blueprint for single points of failure.
3.4. Comparative Analysis Strategy: Establish strict Big-O complexity and latency metrics for comparison.
3.5. Synthesis & Finalization: Formulate the final architectural blueprint.
3.6. Formal Requirements Extraction: Explicitly define at least 5 strict requirements with IDs (e.g., REQ-SW-001) and Pass Criteria.
4. Solution Scenario Exploration
4.1. Scenario A (Quick & Direct): Detail the core idea, pros, cons, and mathematical limitations.
4.2. Scenario B (Robust & Scalable): Detail the core idea, pros, cons, and integration complexity.
4.3. Scenario C (Balanced Hybrid): Detail the trade-off matrix and synergies.
5. Detailed Step-by-Step Execution & Reflection
5.1. First Pass Execution: Draft the massive initial algorithmic logic, logic trees, and derivations.
5.2. Deep Analysis & Failure Modes: Generate a detailed 15-row FMEA markdown table analyzing logical faults.
5.3. Trigger 1 (Verification): Actively find and fix a critical flaw (e.g., memory leak, race condition, math error).
5.4. Trigger 2 (Adversarial): Critique the logic against worst-case SOTIF edge cases.
5.5. Refinement Strategy (Version 2.0): Write the corrected, hardened, production-ready logic.
6. Comparative Analysis & Synthesis
6.1. Comparison Matrix: Draw a 6-row by 5-column markdown comparison table of the scenarios.
6.2. Evaluation of Solution Combinations: Discuss hybrid strengths and emergent capabilities.
6.3. Selection Rationale: Provide a mathematically backed justification for the final choice.
7. Final Solution Formulation
7.1. Executive Summary: One-paragraph highly technical summary of the outcome.
7.2. Detailed Recommended Solution: Plan the exact structure of the final output code.
7.3. Implementation Caveats & Next Steps: Identify hardware-specific deployment risks.
8. Meta-Commentary & Confidence Score
8.1. Final Confidence Score: Rate out of 100 based on rigorous bounds.
8.2. Rationale for Confidence: Justify based on the self-correction loops.
8.3. Limitations of This Analysis: State physical, theoretical, or compute limitations not fully solved.
8.4. Alternative Viewpoints Not Explored: Mention radical paradigm shifts (e.g., ML vs Deterministic logic).
</think>

## 6. GPF Structure
Formal Structure: Generalized Problem Formulation (GPF) - Version 2.1
GPF HEADER
•	Problem ID: A unique, machine-readable identifier (string).
•	Canonical Name: The full, descriptive name of the problem (string).
•	Problem Version: The semantic version "2.1".
•	Last Update Date: {date_str}
•	Estimated Origin Date/Period: Origin period (string).
•	Primary Domain(s): Hierarchical classification string using ::
•	Keywords: A list of keywords (list of strings).
GPF DETAILS (10 Elements)
1. Core Problem Definition & Ontological Scaffolding (Problem Statement, Formal Inputs, Formal Outputs, Task Definition, Ontological Scaffolding)
2. Abstraction Level & Generativity
3. Problem Architecture (MUST INCLUDE >100 LINES XML SYSML)
4. Formal Specification (MUST INCLUDE SET-THEORY MATH AND MASSIVE PYTHON ABC STUB)
5. Evaluation & Verification (MUST INCLUDE COMPLETE PYTHON VERIFIER CODE)
6. Constraints & Context
7. Problem Classification & Scoring
8. Relational Network
9. Exemplars
10. History & Lineage

## 7. QWEN3 MULTI-TURN JSON SCHEMA
Put this exact schema structure into the response window as raw text representing a valid JSON string (array of 1 task):

```json
[
  {{
    "training_data_id": "TD-GPF-{doc_short}-T{turn}t{task_idx}-{date_compact}",
    "prompt_version": "Problems_V1.1",
    "model_used_generation": "Gemini-3.1-pro",
    "knowledge_source_date": "Extract Date YYYY-MM-DD from doc, or write Unknown",
    "document": "{doc_name}",
    "task_type": "formalized_problem",
    "affected_role": "{role}",
    "date_of_generation": "{date_str}",
    "key_words": ["A technical keyword", "Another technical keyword", "A third technical keyword"],
    "summary": "A concise, one-sentence, highly technical summary of the GPF",
    "difficulty": "{diff}",
    "evaluation_criteria": ["A strict technical pass/fail criterion", "Another strict technical criterion"],
    "conversations": [
      {{
        "role": "user",
        "content": "[Thinking] An immersive, in-character 3-paragraph prompt from the assigned role, demanding the formalization of a core engineering challenge into a Generalized Problem Formulation (GPF) version 2.1, based entirely on the assigned Meta-Strategy."
      }},
      {{
        "role": "assistant",
        "reasoning": "The complete, 10000+ character internal monologue strictly following the 8-step template provided, enclosed in <think> and </think> tags.",
        "content": "A fully escaped JSON string representing an object with EXACTLY these 10 keys: 'core_problem_definition' (Narrative and strict I/O objects), 'abstraction_level', 'problem_architecture' (MUST INCLUDE >100 LINES XML SYSML), 'formal_specification' (MUST INCLUDE SET-THEORY MATH AND MASSIVE PYTHON ABC STUB), 'evaluation_verification' (MUST INCLUDE COMPLETE PYTHON VERIFIER CODE), 'constraints_context', 'problem_classification', 'relational_network', 'exemplars', 'history_lineage'."
      }},
      {{
        "role": "user",
        "content": "[No Thinking] An in-character follow-up question inquiring about how the objective function constraints handle stochastic outliers."
      }},
      {{
        "role": "assistant",
        "reasoning": "<think></think>",
        "content": "A brief, highly technical plaintext answer."
      }},
      {{
        "role": "user",
        "content": "[No Thinking] An in-character follow-up question regarding how to adapt the Python verification stub for a different hardware architecture."
      }},
      {{
        "role": "assistant",
        "reasoning": "<think></think>",
        "content": "A brief, highly technical plaintext answer."
      }}
    ]
  }}
]
```
</instructions>"""
    return prompt
'''

# We need to replace the `def build_generation_prompt(variation, turn, task_idx, doc_name, mode, is_soft_retry=False):` function entirely.
pattern = re.compile(r'def build_generation_prompt\(.*?\):.*?return prompt', re.DOTALL | re.MULTILINE)
content = pattern.sub(new_prompt_func, content)

# Now inject the new combined roles into VARIATION_TECHNICAL and VARIATION_REGULATORY
VARIATION_TECHNICAL_STR = '''VARIATION_TECHNICAL = {
    1: [(98, "Theoretical Background", "Lead Systems Eng / Senior Software Architect"),
        (92, "Reverse Engineering", "Data Architect / Senior System Engineer")],
    2: [(95, "Critique of the Approach", "QA Automation Lead / Senior Safety Manager"),
        (89, "Practical Usage", "Hardware Constraints / Senior Validation Eng")],
    3: [(88, "Benchmarking", "Network Engineer / Senior Integration Eng"),
        (94, "Further Improvement", "ML Ops Lead / Senior Project Manager")],
    4: [(97, "Theoretical Background", "Functional Safety / Senior DevOps Engineer"),
        (85, "Reverse Engineering", "Diagnostics Expert / Senior Requirements Eng")],
    5: [(96, "Critique of the Approach", "SOTIF Analyst / Senior Software Architect"),
        (82, "Practical Usage", "Product Manager / Senior System Engineer")],
    6: [(90, "Benchmarking", "Sensor Architect / Senior Safety Manager"),
        (93, "Further Improvement", "CyberSec Engineer / Senior Validation Eng")],
    7: [(91, "Theoretical Background", "Control Systems Eng / Senior Integration Eng"),
        (86, "Reverse Engineering", "Performance Eng / Senior Project Manager")],
    8: [(94, "Critique of the Approach", "Perception Lead / Senior DevOps Engineer"),
        (89, "Practical Usage", "Simulation Engineer / Senior Requirements Eng")],
}'''

VARIATION_REGULATORY_STR = '''VARIATION_REGULATORY = {
    1: [(98, "Constraint Formalization", "Legal Engineer / Senior Software Architect"),
        (92, "Compliance Validation", "Homologation Lead / Senior System Engineer")],
    2: [(95, "Liability Mapping", "Liability Auditor / Senior Safety Manager"),
        (89, "Cross-Jurisdictional Harmonization", "Standards Eng / Senior Validation Eng")],
    3: [(88, "Ambiguity Resolution", "Policy Architect / Senior Integration Eng"),
        (94, "Regulatory Loophole", "Compliance Lead / Senior Project Manager")],
    4: [(97, "Artifact Compliance Audit", "Functional Safety / Senior DevOps Engineer"),
        (85, "Compliance Validation", "Certification Auth / Senior Requirements Eng")],
    5: [(96, "Liability Mapping", "SOTIF Analyst / Senior Software Architect"),
        (82, "Policy Enforcement", "Legal Counsel / Senior System Engineer")],
    6: [(90, "Ambiguity Resolution", "Homologation Eng / Senior Safety Manager"),
        (93, "Artifact Compliance Audit", "Safety Assessor / Senior Validation Eng")],
    7: [(91, "Constraint Formalization", "Regulation Eng / Senior Integration Eng"),
        (86, "Compliance Validation", "Test Manager / Senior Project Manager")],
    8: [(94, "Liability Mapping", "CyberSec Lead / Senior DevOps Engineer"),
        (89, "Cross-Jurisdictional Harmonization", "Systems Architect / Senior Requirements Eng")],
}'''

content = re.sub(r'VARIATION_TECHNICAL = \{.*?\n\}', VARIATION_TECHNICAL_STR, content, flags=re.DOTALL)
content = re.sub(r'VARIATION_REGULATORY = \{.*?\n\}', VARIATION_REGULATORY_STR, content, flags=re.DOTALL)

with open("c:\\Users\\User\\VS_Projects\\Helpers\\Antigravity\\AgenticWorkflowPlaywright_Visuals\\pipeline.py", "w", encoding="utf-8") as f:
    f.write(content)

print("SUCCESS")
