"""
validate_task.py — Comprehensive Quality Gate Validator
=======================================================
Validates a single-task JSON file against ALL quality gates defined in the
DataQualityChecker and CodingTaskGenerator skills.

Exit codes: 0 = PASS, 1 = FAIL
Output: JSON quality report to stdout

Usage:
    python validate_task.py <filepath>
    python validate_task.py <filepath> --save-report <report_path>
    python validate_task.py <filepath> --quiet
"""
import sys
import json
import re
import os


# ── Quality Gate Thresholds ──────────────────────────────────────────────────
COT_MIN_CHARS = 8_000
COT_REGEN_THRESHOLD = 5_000
ANSWER_MIN_CHARS = 15_000
CODE_MIN_LINES = 100
CODE_REGEN_THRESHOLD = 50
REQUIRED_TURNS = 6
MIN_TEST_CRITERIA = 5
MIN_FORMAL_REQUIREMENTS = 5
COPYRIGHT_HEADER = "Copyright by 4QDR.AI"

REQUIRED_TOP_FIELDS = [
    "training_data_id", "prompt_version", "model_used_generation",
    "knowledge_source_date", "document", "task_type", "affected_role",
    "date_of_generation", "key_words", "summary", "difficulty",
    "evaluation_criteria", "conversations"
]

STRUCTURED_ANSWER_KEYS = [
    "core_problem_definition", "abstraction_level", "problem_architecture",
    "formal_specification", "evaluation_verification", "constraints_context",
    "problem_classification", "relational_network", "exemplars", "history_lineage"
]

REQUIRED_GPF_HEADERS = {
    "core_problem_definition": [
        "1. Core Problem Definition",
        "1.1 Problem Statement",
        "1.2 Formal Inputs",
        "1.3 Formal Outputs",
        "1.4 Task Definition",
        "1.5 Ontological Scaffolding"
    ],
    "abstraction_level": [
        "2. Abstraction Level",
        "2.1 Description",
        "2.2 Indicators",
        "2.3 Assigned Abstraction Level"
    ],
    "problem_architecture": [
        "3. Problem Architecture",
        "3.1 Architectural Description",
        "3.2 Formal Architectural Model"
    ],
    "formal_specification": [
        "4. Formal Specification",
        "4.1 Symbolic Representation",
        "4.2 Formal Requirements",
        "4.3 Code Representation"
    ],
    "evaluation_verification": [
        "5. Evaluation",
        "5.1 Success Metrics",
        "5.2 Acceptance Criteria",
        "5.3 Verification Code"
    ],
    "constraints_context": [
        "6. Constraints & Context",
        "6.1 Operational Constraints",
        "6.2 Contextual Assumptions"
    ],
    "problem_classification": [
        "7. Problem Classification",
        "7.1 Problem Type",
        "7.2 Complexity Scoring",
        "7.3 Usefulness Scoring"
    ],
    "relational_network": [
        "8. Relational Network",
        "8.1 Related Concepts",
        "8.2 Related Problems"
    ],
    "exemplars": [
        "9. Exemplars",
        "9.1 Illustrative Input",
        "9.2 Illustrative Solution"
    ],
    "history_lineage": [
        "10. History & Lineage",
        "10.1 Derivation Source",
        "10.2 Version History"
    ]
}

# Parent step headers that MUST also appear in the CoT
COT_PARENT_HEADERS = ["1.", "2.", "3.", "4.", "5.", "6.", "7.", "8."]

COT_SUB_ELEMENTS = [
    "1.1", "1.2",
    "2.1", "2.2", "2.3", "2.4", "2.5",
    "3.1", "3.2", "3.3", "3.4", "3.5", "3.6",
    "4.1", "4.2", "4.3",
    "5.1", "5.2", "5.3", "5.4", "5.5",
    "6.1", "6.2", "6.3",
    "7.1", "7.2", "7.3",
    "8.1", "8.2", "8.3", "8.4"
]

BANNED_VOCABULARY = [
    "the user requests",
    "the document says", "source material", "as mentioned in the pdf",
    "based on the provided", "the text states", "generate a task",
    "generate a multi-turn", "create a coding task", "produce a dataset",
    "cite"
]

# Followup placeholder sentinels that indicate extraction failures
FOLLOWUP_PLACEHOLDERS = [
    "Follow up 1?", "Follow up 2?",
    "Response 1.", "Response 2.",
    "Follow up 1", "Follow up 2",
]

# Instruction-echo sentinels: if these appear in follow-up turn content,
# the model echoed the prompt template instead of generating real content
INSTRUCTION_ECHO_PATTERNS = [
    # Old parenthesized format (kept for legacy/repair prompts)
    "(Write a 2-3 sentence technical inquiry",
    "(Write the first technical response here",
    "(Write another 2-3 sentence",
    "(Write the final technical response here",
    "minimum 100 characters)",
    "Ensure it is highly detailed and contextual.)",
    "Must be highly detailed.)",
    # New angle-bracket format
    "<WRITE YOUR TECHNICAL FOLLOW-UP QUESTION HERE",
    "<WRITE YOUR DETAILED TECHNICAL RESPONSE HERE",
    "<WRITE YOUR SECOND TECHNICAL FOLLOW-UP QUESTION HERE",
    "<WRITE YOUR FINAL TECHNICAL RESPONSE HERE",
    "WRITE YOUR TECHNICAL FOLLOW-UP",
    "NO template text>",
    # Meta-instruction leakage (any format)
    "BANNED VOCABULARY (CRITICAL)",
    "Never say \"based on established practice\"",
    "Never include placeholders like",
    "Every Work Product from VDA/ISO must be treated",
    "(Write the immersive 3-paragraph problem statement here",
]

# JSON key artifact patterns: fragments from LLM treating output as JSON key-value
JSON_KEY_ARTIFACT_PATTERN = r'(?:^|\s)\\?"\s*:\s*\\?"'

# Keywords often used for "Word Salad" padding to inflate character counts
PADDING_KEYWORDS = [
    "visualization", "visualized", "visualize", "visualizations", "visualizing",
    "derivation", "derived", "deriving", "derivations",
    "complexity", "complexities",
    "difficulty", "difficulties",
    "criteria", "criterion",
    "conceptual", "conceptually",
    "initialization", "initialized",
    "virtualized", "virtualization",
]


def validate_task(filepath):
    """Run all quality gates and return structured report."""
    report = {
        "report_id": "QA-AUTO",
        "evaluated_file": os.path.basename(filepath),
        "overall_status": "PASS",
        "locally_fixable": [],       # Issues auto_repair.py can fix
        "needs_regeneration": [],    # Issues requiring full Gemini re-prompt
        "needs_partial_repair": [],  # Issues fixable by re-prompting only follow-up turns
        "metrics": {
            "json_structure": {"status": "PASS", "violations": []},
            "conversation_completeness": {"status": "PASS", "violations": []},
            "richness_and_complexity": {"status": "PASS", "violations": []},
            "structured_answer_format": {"status": "PASS", "violations": []},
            "cot_structure": {"status": "PASS", "violations": []},
            "self_containment": {"status": "PASS", "violations": []},
            "followup_quality": {"status": "PASS", "violations": []},
            "thinking_quality": {"status": "PASS", "violations": []},
        }
    }

    def fail(category, message, fixable_locally=False, partial_repair=False):
        report["overall_status"] = "FAIL"
        report["metrics"][category]["status"] = "FAIL"
        report["metrics"][category]["violations"].append(message)
        if fixable_locally:
            report["locally_fixable"].append({"category": category, "issue": message})
        elif partial_repair:
            report["needs_partial_repair"].append({"category": category, "issue": message})
        else:
            report["needs_regeneration"].append({"category": category, "issue": message})

    def check_keyword_padding(text, turn_label):
        """Check for excessive density of padding keywords (word-salad)."""
        if not text:
            return
        words = re.findall(r'\b\w+\b', text.lower())
        if not words:
            return
        
        # 1. Check density of padding keywords
        padding_count = sum(1 for w in words if w in PADDING_KEYWORDS)
        density = padding_count / len(words)
        if density > 0.15:  # Absolute density threshold
            fail("richness_and_complexity",
                 f"{turn_label} contains keyword-salad padding "
                 f"({padding_count}/{len(words)} padding words, {density:.1%})",
                 fixable_locally=False)
            return

        # 2. Check for "dense clusters" (3+ keywords in a window of 5)
        for i in range(len(words) - 4):
            window = words[i:i+5]
            win_padding = sum(1 for w in window if w in PADDING_KEYWORDS)
            if win_padding >= 4:
                fail("richness_and_complexity",
                     f"{turn_label} contains a dense cluster of padding keywords "
                     f"(e.g., '{' '.join(window)}')",
                     fixable_locally=False)
                return

    def check_internal_repetition(text, turn_label):
        """Check for verbatim repeated paragraphs or large blocks (looping)."""
        if not text or len(text) < 1000:
            return
        paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 100]
        if not paragraphs:
            return
            
        seen_sigs = {}
        for i, p in enumerate(paragraphs):
            # Signature: first 150 chars normalized
            sig = re.sub(r'\s+', '', p[:150].lower())
            if sig in seen_sigs:
                fail("richness_and_complexity",
                     f"{turn_label} contains a verbatim repetition loop. "
                     f"Paragraph {i} matches paragraph {seen_sigs[sig]}.",
                     fixable_locally=False)
                return
            seen_sigs[sig] = i

    # ── Gate 0: JSON Parsing ─────────────────────────────────────────────
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        fail("json_structure", f"JSON parse error: {e}", fixable_locally=True)
        return report
    except FileNotFoundError:
        fail("json_structure", f"File not found: {filepath}")
        return report

    if not isinstance(data, list) or len(data) == 0:
        fail("json_structure", "Expected non-empty JSON array")
        return report

    task = data[0]
    if not isinstance(task, dict):
        fail("json_structure", "First element is not a JSON object")
        return report

    # ── Gate 1: Top-Level Fields ─────────────────────────────────────────
    for field in REQUIRED_TOP_FIELDS:
        if field not in task:
            fail("json_structure", f"Missing required field: '{field}'", fixable_locally=True)

    # ── Gate 2: Conversation Structure ───────────────────────────────────
    convs = task.get("conversations", [])
    if not isinstance(convs, list):
        fail("conversation_completeness", "conversations is not an array")
        return report

    if len(convs) != REQUIRED_TURNS:
        fail("conversation_completeness",
             f"Expected {REQUIRED_TURNS} turns, got {len(convs)}",
             fixable_locally=(len(convs) < REQUIRED_TURNS))

    # Check role alternation: user, assistant, user, assistant, user, assistant
    expected_roles = ["user", "assistant", "user", "assistant", "user", "assistant"]
    for i, (conv, expected_role) in enumerate(zip(convs, expected_roles)):
        if not isinstance(conv, dict):
            fail("conversation_completeness", f"Turn {i}: expected a JSON object but got a different type")
            continue
        actual_role = conv.get("role", "")
        if actual_role != expected_role:
            fail("conversation_completeness",
                 f"Turn {i}: expected role '{expected_role}', got '{actual_role}'")

    # Check non-empty content for all turns
    for i, conv in enumerate(convs):
        if not isinstance(conv, dict):
            continue
        content = conv.get("content", "")
        if not content or not content.strip():
            # Followup assistant turns (3 and 5) with empty content need full regeneration
            if conv.get("role") == "assistant" and i in [3, 5]:
                fail("conversation_completeness",
                     f"Turn {i}: empty assistant content (last followup response is blank) — requires regeneration",
                     fixable_locally=False)
            elif conv.get("role") == "assistant" and i > 1:
                fail("conversation_completeness",
                     f"Turn {i}: empty content",
                     fixable_locally=True)
            else:
                fail("conversation_completeness",
                     f"Turn {i}: empty content",
                     fixable_locally=False)

    # Check <think></think> format for No-Thinking assistant turns (indices 3, 5)
    for i in [3, 5]:
        if i < len(convs):
            conv = convs[i]
            if isinstance(conv, dict) and conv.get("role") == "assistant":
                reasoning = conv.get("reasoning", "")
                if reasoning != "<think></think>":
                    if not reasoning or reasoning.strip() == "":
                        fail("conversation_completeness",
                             f"Turn {i}: missing <think></think> tags (got empty reasoning)",
                             fixable_locally=True)

    if len(convs) < 2:
        return report  # Can't check further without main assistant turn

    # ── Gate 3: Main Assistant Turn (index 1) — Richness ─────────────────
    main_assistant = convs[1]
    reasoning = main_assistant.get("reasoning", "")
    content = main_assistant.get("content", "")

    # ── Gate 3a: Empty or Placeholder Thinking Check ──────────────────────
    # Detect [NO_THINKING_SECTION] placeholder or a completely empty reasoning field.
    # Both indicate the LLM failed to produce a real CoT monologue.
    EMPTY_THINKING_SENTINELS = [
        "[NO_THINKING_SECTION]",
        "[no_thinking_section]",
        "<think></think>",   # Empty self-closed tags
    ]
    reasoning_stripped = reasoning.strip()
    if not reasoning_stripped:
        fail("richness_and_complexity",
             "Main assistant turn (index 1): reasoning field is completely empty — requires regeneration",
             fixable_locally=False)
    else:
        for sentinel in EMPTY_THINKING_SENTINELS:
            if reasoning_stripped == sentinel or reasoning_stripped.startswith("[NO_THINKING_SECTION]"):
                fail("richness_and_complexity",
                     f"Main assistant turn (index 1): reasoning contains placeholder '{sentinel}' instead of real CoT — requires regeneration",
                     fixable_locally=False)
                break

    # Check for merged content-in-reasoning anomaly
    if len(content.strip()) < 100 and "</think>" in reasoning:
        parts = reasoning.split("</think>", 1)
        if len(parts) == 2 and len(parts[1].strip()) > 100:
            fail("richness_and_complexity",
                 f"Content merged into reasoning ({len(parts[1])} chars after </think>)",
                 fixable_locally=True)
            # For length checks below, use the actual content length
            content = parts[1].strip()

    cot_len = len(reasoning)
    content_len = len(content)

    if cot_len < COT_MIN_CHARS:
        # User requested: regen below 9000
        needs_regen = (cot_len < COT_REGEN_THRESHOLD)
        fail("richness_and_complexity",
             f"CoT too short: {cot_len} chars (min {COT_MIN_CHARS})",
             fixable_locally=not needs_regen)

    if content_len < ANSWER_MIN_CHARS:
        fail("richness_and_complexity",
             f"Answer too short: {content_len} chars (min {ANSWER_MIN_CHARS})")

    # Check for forbidden placeholder patterns
    if re.search(r'\.{4,}', content):
        fail("richness_and_complexity",
             "Found forbidden placeholder (4+ dots) in content")

    # ── Gate 4: Structured Answer Format ─────────────────────────────────
    try:
        parsed_answer = json.loads(content)
        if isinstance(parsed_answer, dict):
            for key in STRUCTURED_ANSWER_KEYS:
                if key not in parsed_answer:
                    fail("structured_answer_format",
                         f"Missing structured answer key: '{key}'",
                         fixable_locally=True)
            
            # Explicit Header & Enumeration Validation (fuzzy matching)
            # Gemini may output "1.1 Problem Statement (Narrative):" instead of
            # exactly "1.1 Problem Statement", so we match by numeric prefix + keyword.
            def _header_present(header_text, section_text):
                """Check if a header is present using fuzzy matching."""
                section_lower = section_text.lower()
                # Direct exact match first
                if header_text in section_text:
                    return True
                # Extract numeric prefix (e.g. "1.", "1.1", "10.2")
                num_match = re.match(r'^(\d+\.[\d.]*)\s*(.*)', header_text)
                if num_match:
                    num_prefix = num_match.group(1).rstrip('.')
                    title_words = num_match.group(2).strip().lower()
                    # Check if the numeric prefix exists in the section
                    # e.g., look for "1.1" or "1.1 " anywhere in text
                    if num_prefix in section_text:
                        # For parent headers (like "1. Core Problem Definition"),
                        # having the subsections (1.1, 1.2, etc.) is sufficient
                        if '.' not in num_prefix:
                            # Parent header — accept if ANY subsection exists
                            sub_prefix = num_prefix + "."
                            if sub_prefix in section_text:
                                return True
                        # Extract first significant keyword (>3 chars)
                        keywords = [w for w in title_words.split() if len(w) > 3]
                        if keywords:
                            # Check if at least one keyword is near the prefix
                            for kw in keywords[:2]:
                                if kw.replace('&', 'and') in section_lower:
                                    return True
                        else:
                            # No keywords to check, prefix alone is sufficient
                            return True
                return False

            for key, expected_headers in REQUIRED_GPF_HEADERS.items():
                section_data = parsed_answer.get(key, "")
                section_str = json.dumps(section_data) if isinstance(section_data, dict) else str(section_data)
                for header in expected_headers:
                    if not _header_present(header, section_str):
                        fail("structured_answer_format", 
                             f"Missing enumerated header '{header}' in section '{key}'.",
                             fixable_locally=False)

            # ── Gate 4a: GPF specific Python ABC check ─────────────────────────
            formal_spec = parsed_answer.get("formal_specification", "")
            if isinstance(formal_spec, str):
                if "class " not in formal_spec and "def " not in formal_spec:
                    fail("structured_answer_format", "formal_specification code_representation missing Python class/def definitions")
            else:
                fail("structured_answer_format", "formal_specification is not a string block")

            # ── Gate 4b: GPF specific XML SysML check ─────────────────────────
            prob_arch = parsed_answer.get("problem_architecture", "")
            if isinstance(prob_arch, str):
                has_xml = ("<" in prob_arch or "\\<" in prob_arch or "&lt;" in prob_arch
                           or "xmi:" in prob_arch.lower() or "sysml" in prob_arch.lower())
                if not has_xml:
                    fail("structured_answer_format", "problem_architecture missing XML/XMI representation")
                else:
                    xml_lines = prob_arch.count("\\n") + prob_arch.count("\n") + 1
                    if xml_lines < 30:
                         fail("richness_and_complexity", f"XML SysML too short: ~{xml_lines} lines")
            else:
                fail("structured_answer_format", "problem_architecture is not a string block")

            # ── Gate 4c: GPF Evaluation Code check ─────────────────────────
            eval_verif = parsed_answer.get("evaluation_verification", "")
            if isinstance(eval_verif, str):
                if "def " not in eval_verif:
                    fail("structured_answer_format", "evaluation_verification missing Python verification logic")
            else:
                 fail("structured_answer_format", "evaluation_verification is not a string block")
        else:
            fail("structured_answer_format",
                 "Content is valid JSON but not an object (expected dict with 6 keys)",
                 fixable_locally=True)
    except (json.JSONDecodeError, TypeError):
        # Content is not JSON — might be raw markdown
        fail("structured_answer_format",
             "Content is not a valid JSON object (may be raw markdown)",
             fixable_locally=True)

    # ── Gate 5: CoT 8-Step Structure ─────────────────────────────────────
    # Extract think block content
    think_match = re.search(r'<think>(.*?)</think>', reasoning, re.DOTALL)
    think_content = think_match.group(1) if think_match else reasoning

    # Normalize: convert escaped \\n sequences to actual newlines for regex matching
    think_normalized = think_content.replace("\\n", "\n").replace("\\\\n", "\n")
    # Collapse multiple horizontal spaces to single spaces to allow matching against Gemini's double-spaced lists
    think_normalized = re.sub(r'[ \t]+', ' ', think_normalized)

    # ── Gate 5a: Check parent step headers (1. through 8.) ───────────────
    missing_parents = []
    for parent in COT_PARENT_HEADERS:
        # Match e.g. "1." or "**1.**" or "### 1." at start of line
        pattern = rf'(?:^|[\n\r])[\s#\-\*]*{re.escape(parent)}[\s]'
        if not re.search(pattern, think_normalized):
            missing_parents.append(parent)

    if missing_parents:
        fail("cot_structure",
             f"Missing CoT parent headers: {', '.join(missing_parents)}",
             fixable_locally=False)

    # ── Gate 5b: Check sub-elements (1.1 through 8.4) ────────────────────
    missing_elements = []
    for elem in COT_SUB_ELEMENTS:
        # Flexible pattern to match headers like: "1.1.", "**1.1.**", "### 1.1", "- 1.1:"
        pattern = rf'(?:^|[\n\r])[\s#\-\*]*{re.escape(elem)}[\.\s:\)]'
        if not re.search(pattern, think_normalized):
            missing_elements.append(elem)

    if missing_elements:
        # User Optimization: If the CoT is very long (>15k), allow up to 5 missing sub-elements as fixable
        is_fixable = (cot_len > 15_000 and len(missing_elements) <= 5)
        
        if len(missing_elements) <= 5:
            fail("cot_structure",
                 f"Missing CoT sub-elements: {', '.join(missing_elements)}",
                 fixable_locally=is_fixable)
        else:
            fail("cot_structure",
                 f"Missing {len(missing_elements)} CoT sub-elements: "
                 f"{', '.join(missing_elements[:5])}...",
                 fixable_locally=False)

    # ── Gate 5c: Duplicate <think> tag detection ─────────────────────────
    # Detect patterns like <think>\n<think> or <think>\n\<think\>
    dup_think = re.search(r'<think>\s*(?:\\?<think\\?>|<think>)', reasoning)
    if dup_think:
        fail("cot_structure",
             "Duplicate <think> tag detected inside reasoning",
             fixable_locally=True)

    # ── Gate 6: Self-Containment (Immersion) ─────────────────────────────
    full_text = (reasoning + " " + content).lower()
    for banned in BANNED_VOCABULARY:
        if banned.lower() in full_text:
            fail("self_containment",
                 f"Banned vocabulary detected: '{banned}'",
                 fixable_locally=True)

    # ── Gate 7: Followup Placeholder Detection ───────────────────────────
    # Detect when extraction produced fallback placeholder text
    for idx in [2, 3, 4, 5]:  # Follow-up turns
        if idx < len(convs):
            conv_content = convs[idx].get("content", "").strip()
            for placeholder in FOLLOWUP_PLACEHOLDERS:
                if conv_content == placeholder:
                    fail("conversation_completeness",
                         f"Turn {idx}: contains extraction placeholder '{placeholder}'",
                         fixable_locally=False)

    # ── Gate 8: Follow-up Specificity (User turns 2, 4) ──────────────────
    for idx in [2, 4]:  # User follow-up turns
        if idx < len(convs) and convs[idx].get("role") == "user":
            fu_content = convs[idx].get("content", "")
            if len(fu_content) < 100:
                fail("conversation_completeness",
                     f"Turn {idx}: follow-up user prompt too short ({len(fu_content)} chars, min 100)",
                     fixable_locally=False)

    # ── Gate 9: [Thinking]/[No Thinking] Prefix Check ────────────────────
    # Turn 0 (user) must start with [Thinking]
    if len(convs) > 0 and convs[0].get("role") == "user":
        t0_content = convs[0].get("content", "")
        if not t0_content.startswith("[Thinking]"):
            fail("conversation_completeness",
                 "Turn 0: user prompt must start with '[Thinking]'",
                 fixable_locally=True)
    # Turns 2, 4 (user) must start with [No Thinking]
    for idx in [2, 4]:
        if idx < len(convs) and convs[idx].get("role") == "user":
            tu_content = convs[idx].get("content", "")
            if not tu_content.startswith("[No Thinking]"):
                fail("conversation_completeness",
                     f"Turn {idx}: user prompt must start with '[No Thinking]'",
                     fixable_locally=True)

    # ── Gate 10: Anti-Repetition (cross-element sentence dedup) ────────────
    try:
        parsed_for_rep = json.loads(content)
        if isinstance(parsed_for_rep, dict):
            # Check for repeated sentences across all string-block elements
            all_sentences = []
            for key in STRUCTURED_ANSWER_KEYS:
                block_text = str(parsed_for_rep.get(key, ""))
                # Split on sentence-ending punctuation
                sentences = [s.strip() for s in re.split(r'[.!?]\s', block_text) if len(s.strip()) > 80]
                all_sentences.extend(sentences)
            if len(all_sentences) > 1:
                seen = {}
                dup_count = 0
                for i, s in enumerate(all_sentences):
                    sig = re.sub(r'\s+', '', s[:120].lower())
                    if sig in seen:
                        dup_count += 1
                        if dup_count >= 2:  # Allow one near-match; flag on 2+ duplicates
                            fail("structured_answer_format",
                                 f"Multiple duplicate sentences detected across GPF elements ({dup_count} duplicates found)",
                                 fixable_locally=False)
                            break
                    seen[sig] = i
    except (json.JSONDecodeError, TypeError):
        pass  # Already caught in Gate 4

    # ── Gate 11: Keyword-Salad Padding and Internal Repetition ────────────
    # Check main reasoning and follow-up user turns
    check_keyword_padding(reasoning, "Reasoning (CoT)")
    check_internal_repetition(reasoning, "Reasoning (CoT)")
    
    for i, conv in enumerate(convs):
        if conv.get("role") == "user":
            check_keyword_padding(conv.get("content", ""), f"Turn {i} (user)")

    # ── Gate 12: [No Thinking] Tag Duplication ────────────────────────────
    # Detect doubled [No Thinking] prefix with JSON key artifacts between them
    for idx in [2, 4]:  # User follow-up turns
        if idx < len(convs) and convs[idx].get("role") == "user":
            fu_content = convs[idx].get("content", "")
            # Pattern: [No Thinking] ... [No Thinking] (doubled prefix)
            nt_count = fu_content.count("[No Thinking]")
            if nt_count > 1:
                fail("followup_quality",
                     f"Turn {idx}: duplicated [No Thinking] prefix ({nt_count} occurrences)",
                     fixable_locally=True)

    # ── Gate 13: Instruction Echo Detection (Follow-Up Turns) ─────────────
    # Detect when model echoed the prompt template instead of generating real content
    for idx in [2, 3, 4, 5]:  # All follow-up turns
        if idx < len(convs):
            fu_content = convs[idx].get("content", "")
            for echo_pattern in INSTRUCTION_ECHO_PATTERNS:
                if echo_pattern in fu_content:
                    fail("followup_quality",
                         f"Turn {idx}: instruction echo detected — model echoed prompt template "
                         f"instead of generating content (matched: '{echo_pattern[:50]}...')",
                         partial_repair=True)
                    break  # One match per turn is enough

    # ── Gate 14: JSON Key Artifact Detection ──────────────────────────────
    # Detect JSON key fragments at START of content (first 50 chars) to avoid false positives
    for idx in [0, 2, 3, 4, 5]:  # Skip index 1 (main assistant JSON)
        if idx >= len(convs):
            continue
        conv_content = convs[idx].get("content", "")
        # Only check FIRST 50 chars of content to avoid false positives on technical text
        content_head = conv_content.strip()[:50]
        if re.search(r'\\?"\s*:\s*\\?"\[', content_head):
            fail("followup_quality",
                 f"Turn {idx}: JSON key artifact detected at content start",
                 fixable_locally=True)
        # Also check for the specific pattern: content starts with \": \"
        if content_head.startswith('\\"') or content_head.startswith('": "'):
            fail("followup_quality",
                 f"Turn {idx}: content starts with JSON key artifact",
                 fixable_locally=True)

    # ── Gate 15: [No Thinking] Tag Leaking into Assistant Content ─────────
    # [No Thinking] is a USER-ONLY prefix. If it appears in assistant turns, it's a generation error.
    for idx in [1, 3, 5]:  # Assistant turns (0-indexed: Turn 2, Turn 4, Turn 6)
        if idx < len(convs) and convs[idx].get("role") == "assistant":
            asst_content = convs[idx].get("content", "")
            if isinstance(asst_content, str) and asst_content.strip().startswith("[No Thinking]"):
                fail("followup_quality",
                     f"Turn {idx}: assistant content starts with '[No Thinking]' — this tag is for USER turns only",
                     partial_repair=True)

    # ── Gate 16: COT Meta-Generation Detection ────────────────────────────
    # Detect if the COT/reasoning describes task generation instead of problem solving
    META_COT_PATTERNS = [
        "the request is to generate",
        "i need to generate",
        "i will structure the user turn",
        "i need to create a task",
        "the meta-strategy is",
        "the document classification is",
        "the variation schema",
        "i will generate",
        "creating a coding task",
        "to generate a multi-turn",
        "produce a dataset",
        "generate exactly 1 distinct",
    ]
    reasoning_lower = reasoning.lower()
    meta_cot_hits = []
    for pat in META_COT_PATTERNS:
        if pat in reasoning_lower:
            meta_cot_hits.append(pat)
    if len(meta_cot_hits) >= 2:  # Allow 1 borderline match, flag on 2+
        fail("thinking_quality",
             f"COT describes task generation instead of problem solving. "
             f"Meta-generation phrases found: {meta_cot_hits[:5]}",
             fixable_locally=False)

    # ── Gate 17: Raw Thinking File Integrity ──────────────────────────────
    # Check the auxiliary thinking.txt file for extraction failures or emptiness.
    # FALLBACK: If thinking.txt extraction failed but the JSON reasoning field
    # has rich content (>500 chars), treat as a soft warning, not a hard fail.
    # The thinking.txt captures Gemini's UI panel; the JSON reasoning field
    # captures the instructed <think> output — they are complementary.
    try:
        json_dir = os.path.dirname(os.path.abspath(filepath))
        base_name = os.path.splitext(os.path.basename(filepath))[0]
        output_dir = os.path.dirname(json_dir)
        thinking_dir = os.path.join(output_dir, "thinking")
        thinking_path = os.path.join(thinking_dir, f"{base_name}.txt")

        # Check JSON reasoning field length as fallback
        json_reasoning_len = len(reasoning) if reasoning else 0
        has_rich_json_reasoning = json_reasoning_len > 500

        if os.path.exists(thinking_path):
            with open(thinking_path, 'r', encoding='utf-8', errors='replace') as tf:
                raw_think = tf.read().strip()
                
            fail_markers = ["[NO_THINKING_SECTION]", "[EXTRACTION_FAILED]", "[EXTRACTION_ERROR]"]
            thinking_file_failed = False
            for marker in fail_markers:
                if marker in raw_think:
                    thinking_file_failed = True
                    break
            
            thinking_file_undersized = (not raw_think or len(raw_think) < 100)

            if thinking_file_failed or thinking_file_undersized:
                if has_rich_json_reasoning:
                    # JSON reasoning is rich — thinking.txt failure is non-critical
                    pass  # Soft pass: UI extraction failed but JSON reasoning is intact
                else:
                    # Both sources are bad — hard fail
                    if thinking_file_failed:
                        for marker in fail_markers:
                            if marker in raw_think:
                                fail("thinking_quality", 
                                     f"Internal thinking monologue extraction failed: {marker}", 
                                     fixable_locally=False)
                                break
                    else:
                        fail("thinking_quality", 
                             f"Internal thinking monologue is critically undersized ({len(raw_think)} chars)", 
                             fixable_locally=False)
        else:
            if not has_rich_json_reasoning:
                fail("thinking_quality", "Missing auxiliary thinking.txt file", fixable_locally=False)

    except Exception as e:
        pass

    # ── Gate 18: Per-Element Minimum Length ────────────────────────────────
    ELEMENT_MIN_LENGTHS = {
        "core_problem_definition": 1500,
        "abstraction_level": 300,
        "problem_architecture": 2000,
        "formal_specification": 2500,
        "evaluation_verification": 1500,
        "constraints_context": 400,
        "problem_classification": 300,
        "relational_network": 300,
        "exemplars": 400,
        "history_lineage": 200,
    }
    try:
        parsed_elements = json.loads(content)
        if isinstance(parsed_elements, dict):
            for elem_key, min_len in ELEMENT_MIN_LENGTHS.items():
                elem_text = str(parsed_elements.get(elem_key, ""))
                if len(elem_text) < min_len:
                    fail("richness_and_complexity",
                         f"GPF element '{elem_key}' too short: {len(elem_text)} chars (min {min_len})",
                         fixable_locally=False)
    except (json.JSONDecodeError, TypeError):
        pass

    # ── Gate 19: Mathematical Notation Density ─────────────────────────────
    MATH_SYMBOLS = [
        # Unicode math symbols
        "∀", "∃", "∈", "∉", "⊂", "⊆", "⊃", "⊇", "∪", "∩",
        "→", "←", "↔", "⇒", "⇐", "⇔",
        "∑", "∏", "∫", "∂",
        # LaTeX notation
        "\\forall", "\\exists", "\\in", "\\subset", "\\sum",
        "$", "\\(", "\\)",
        # Common optimization / set theory keywords
        "argmin", "argmax", "inf ", "sup ",
        # ASCII math patterns Gemini commonly outputs
        "subset", "not in", "R^", "R+", "R^n",
        "->", "<=", ">=", "!=", "==",
        "iff ", "f(", "g(", "J(", "K(", "C(",
        "Eq ", "Let ",
    ]
    try:
        parsed_math = json.loads(content)
        if isinstance(parsed_math, dict):
            formal_spec_text = str(parsed_math.get("formal_specification", ""))
            math_count = sum(1 for sym in MATH_SYMBOLS if sym in formal_spec_text)
            if math_count < 3:
                fail("richness_and_complexity",
                     f"formal_specification lacks mathematical notation: only {math_count} formal symbols found (min 3)",
                     fixable_locally=False)
    except (json.JSONDecodeError, TypeError):
        pass

    # Add enriched summary stats to report
    code_lines_stat = 0
    test_criteria_stat = 0
    formal_req_stat = 0
    math_symbols_stat = 0
    try:
        parsed_stats = json.loads(content)
        if isinstance(parsed_stats, dict):
            # XML SysML line count from string block
            prob_arch_str = str(parsed_stats.get("problem_architecture", ""))
            code_lines_stat = prob_arch_str.count("\\n") + prob_arch_str.count("\n") + 1
            
            # Count REQ-IDs in formal_specification string
            formal_spec_str = str(parsed_stats.get("formal_specification", ""))
            formal_req_stat = len(re.findall(r'REQ-[A-Z]+-\d+', formal_spec_str))
            
            # Count def/class in evaluation_verification string
            eval_str = str(parsed_stats.get("evaluation_verification", ""))
            test_criteria_stat = eval_str.count("def ") + eval_str.count("assert ")
            
            # Count math symbols
            math_symbols_stat = sum(1 for sym in MATH_SYMBOLS if sym in formal_spec_str)
    except (json.JSONDecodeError, TypeError):
        pass

    report["stats"] = {
        "cot_chars": cot_len,
        "answer_chars": content_len,
        "xml_sysml_lines": code_lines_stat,
        "test_criteria_count": test_criteria_stat,
        "formal_req_count": formal_req_stat,
        "math_symbols_count": math_symbols_stat,
        "turns": len(convs),
    }

    return report


def main():
    quiet = "--quiet" in sys.argv

    if len(sys.argv) < 2:
        if not quiet:
            print(json.dumps({"overall_status": "FAIL", "error": "No filepath provided"}))
        sys.exit(1)

    filepath = sys.argv[1]
    report = validate_task(filepath)

    # Optionally save report to file
    if "--save-report" in sys.argv:
        idx = sys.argv.index("--save-report")
        if idx + 1 < len(sys.argv):
            report_path = sys.argv[idx + 1]
            os.makedirs(os.path.dirname(report_path), exist_ok=True)
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2)

    print(json.dumps(report, indent=2))
    sys.exit(0 if report["overall_status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
