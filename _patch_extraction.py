"""Patch script: Replace validate_and_save_json with block-first extraction."""
import os

filepath = r'c:\Users\User\VS_Projects\Helpers\Antigravity\AgenticWorkflowPlaywright_Visuals\run_gemini_playwright_v2.py'

with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find function boundaries
start_idx = None
end_idx = None
for i, line in enumerate(lines):
    if 'def validate_and_save_json(' in line and start_idx is None:
        start_idx = i
    if 'def run_gemini(' in line and start_idx is not None:
        end_idx = i
        break

print(f"Replacing lines {start_idx+1} to {end_idx} (original function)")

new_function = r'''def validate_and_save_json(llm_response, out_json_path, thinking_text=None):
    """Assemble the granular semantic blocks into a valid 6-turn conversational JSON.
    
    Uses block-first extraction (same architecture as the reference project):
    1. Extract !!!!!BLOCK-NAME!!!!! blocks from raw LLM response
    2. Parse METADATA block -> metadata dict
    3. Parse REASONING block -> reasoning string  
    4. Parse each GPF-* block -> build assistant_content_obj
    5. Read TURN-3 through TURN-6 blocks -> follow-up turns
    6. Manually construct conversations array
    7. Save clean JSON
    """
    try:
        import json_repair
        
        # 0. Unescape markdown backslash sequences from DOM scraping
        llm_response = unescape_markdown(llm_response)
        
        # 0a. Multi-pass: handle double/triple escaped backslash-underscores
        for _ in range(3):
            if '\\_' not in llm_response:
                break
            llm_response = llm_response.replace('\\_', '_')
        
        # 0b. Normalize line endings
        llm_response = llm_response.replace('\r\r\n', '\n').replace('\r\n', '\n')
        
        # 0c. Clean repetition loops
        llm_response = clean_repetitive_text(llm_response)

        # -- STEP 1: Primary Block Extraction --
        blocks = extract_semantic_blocks(llm_response)
        
        # -- STEP 2: Heuristic Fallback --
        if not blocks or len(blocks) < 5:
            log("⚠️ Insufficient semantic blocks found. Invoking heuristic recovery...")
            h_blocks = heuristic_extract_blocks(llm_response)
            for k, v in h_blocks.items():
                if k not in blocks or len(blocks.get(k, "")) < 50:
                    blocks[k] = v
        
        if not blocks:
            log("❌ FATAL: No semantic blocks recovered even with heuristics.")
            return False
        
        log(f"📦 Extracted {len(blocks)} blocks: {', '.join(sorted(blocks.keys()))}")

        # -- STEP 3: Parse Metadata --
        metadata_raw = clean_semantic_block(blocks.get("METADATA", "{}"))
        try:
            metadata = json_repair.loads(metadata_raw)
        except:
            metadata = {}
        
        if not isinstance(metadata, dict):
            metadata = {}

        # -- STEP 4: Parse Reasoning --
        reasoning_main = clean_semantic_block(blocks.get("REASONING", "(Missing REASONING block)"))
        # Restore CoT numbers stripped by browser OL rendering
        reasoning_main = restore_ol_numbering(reasoning_main)
        # Strip think tags to prevent doubling (we wrap them later)
        reasoning_main = re.sub(r'\\?</?think\\?>', '', reasoning_main, flags=re.IGNORECASE).strip()

        # -- STEP 5: Build GPF Content Object --
        gpf_header = clean_semantic_block(blocks.get("GPF-HEADER", ""))
        core_problem_raw = clean_semantic_block(blocks.get("GPF-PROBLEM-DEFINITION", ""))
        if gpf_header and core_problem_raw:
            core_problem_definition = f"GPF HEADER\n{gpf_header}\n\n{core_problem_raw}"
        elif gpf_header:
            core_problem_definition = f"GPF HEADER\n{gpf_header}"
        else:
            core_problem_definition = core_problem_raw

        assistant_content_obj = {
            "core_problem_definition": core_problem_definition,
            "abstraction_level": clean_semantic_block(blocks.get("GPF-ABSTRACTION-LEVEL", "")),
            "problem_architecture": clean_semantic_block(blocks.get("GPF-ARCHITECTURE", "")),
            "formal_specification": clean_semantic_block(blocks.get("GPF-FORMAL-SPECIFICATION", "")),
            "evaluation_verification": clean_semantic_block(blocks.get("GPF-EVALUATION", "")),
            "constraints_context": clean_semantic_block(blocks.get("GPF-CONSTRAINTS", "")),
            "problem_classification": clean_semantic_block(blocks.get("GPF-CLASSIFICATION", "")),
            "relational_network": clean_semantic_block(blocks.get("GPF-RELATIONAL-NETWORK", "")),
            "exemplars": clean_semantic_block(blocks.get("GPF-EXEMPLARS", "")),
            "history_lineage": clean_semantic_block(blocks.get("GPF-HISTORY", "")),
        }
        
        # Log per-element sizes for debugging
        for elem, val in assistant_content_obj.items():
            log(f"  GPF element {elem}: {len(val)} chars")

        # -- STEP 6: Parse Follow-Up Turns --
        def _strip_escaped_think(text):
            text = re.sub(r'\\?</?think\\?>', '', text, flags=re.IGNORECASE).strip()
            return text
        
        turn1 = clean_semantic_block(blocks.get("TURN-1-USER", "Problem statement missing."))
        turn3 = clean_semantic_block(blocks.get("TURN-3-USER", "How does this handle edge cases?"))
        turn4 = _strip_escaped_think(clean_semantic_block(blocks.get("TURN-4-ASSISTANT", "Logic verified.")))
        turn5 = clean_semantic_block(blocks.get("TURN-5-USER", "Follow up 2?"))
        turn6 = _strip_escaped_think(clean_semantic_block(blocks.get("TURN-6-ASSISTANT", "Response 2.")))
        
        # -- STEP 7: Build 6-Turn Conversations Array --
        conversations = [
            {"role": "user", "content": turn1},
            {
                "role": "assistant", 
                "reasoning": f"<think>\n{reasoning_main}\n</think>",
                "content": json.dumps(assistant_content_obj, indent=2, ensure_ascii=False)
            },
            {"role": "user", "content": turn3},
            {
                "role": "assistant",
                "reasoning": "<think></think>",
                "content": turn4
            },
            {"role": "user", "content": turn5},
            {
                "role": "assistant",
                "reasoning": "<think></think>",
                "content": turn6
            }
        ]

        final_task = metadata.copy()
        final_task["conversations"] = conversations
        if "task_type" not in final_task: final_task["task_type"] = "formalized_problem"
        
        data = [final_task]

        # Quality guard: don't overwrite a better existing file
        if os.path.exists(out_json_path):
            try:
                with open(out_json_path, 'r', encoding='utf-8') as ef:
                    existing_data = json.load(ef)
                if isinstance(existing_data, list) and len(existing_data) > 0:
                    existing_item = existing_data[0]
                    new_item = data[0]
                    existing_meta = len([k for k in existing_item.keys() if k != 'conversations'])
                    new_meta = len([k for k in new_item.keys() if k != 'conversations'])
                    if existing_meta > new_meta + 2:
                        log(f"⚠️ Block extraction WORSE than existing (meta: {new_meta} vs {existing_meta}). Keeping existing.")
                        return True
            except Exception:
                pass

        with open(out_json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        
        log(f"✅ Assembly Success! Saved to {os.path.basename(out_json_path)}")
        return True

    except Exception as e:
        log(f"❌ Assembling failed: {e}")
        import traceback
        log(traceback.format_exc())
        return False

'''

# Replace lines
new_lines = lines[:start_idx] + [new_function + '\n\n'] + lines[end_idx:]

with open(filepath, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"SUCCESS: Replaced validate_and_save_json function")
print(f"New file: {sum(1 for _ in open(filepath, 'r', encoding='utf-8'))} lines")
