import re

file_path = r"c:\Users\User\VS_Projects\Helpers\Antigravity\AgenticWorkflowPlaywright_Visuals\run_gemini_playwright_v2.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update the code_block_directive
new_code_block_directive = '''
    code_block_directive = """
---
CRITICAL OUTPUT FORMAT DIRECTIVE:
You MUST output your response strictly adhering to the JSON array schema provided.
Do NOT use Canvas mode, Gems, or side-by-side environments.
"""
'''
content = re.sub(r'    code_block_directive = """\n---\nCRITICAL OUTPUT FORMAT DIRECTIVE:.*?\]\n"""\n', new_code_block_directive, content, flags=re.DOTALL)
content = re.sub(r'    code_block_directive = """\n---\nCRITICAL OUTPUT FORMAT DIRECTIVE:.*?\n"""\n', new_code_block_directive, content, flags=re.DOTALL)

# 2. Add JSON direct extraction at the start of validate_and_save_json
# Let's find validate_and_save_json

json_extract_patch = '''def validate_and_save_json(llm_response, out_json_path, thinking_text=None):
    """Assemble the granular semantic blocks into a valid 6-turn conversational JSON."""
    try:
        import json_repair
        
        # 0. Clean repetition loops first
        llm_response = clean_repetitive_text(llm_response)

        # NEW LOGIC: Attempt to extract JSON directly
        json_match = re.search(r'\\[\\s*\\{.*?\\}\\s*\\]', llm_response, re.DOTALL)
        if json_match:
            try:
                data = json_repair.loads(json_match.group(0))
                if isinstance(data, list) and len(data) > 0 and "conversations" in data[0]:
                    log("✅ Direct JSON extraction successful!")
                    # Check and fix thinking string
                    for conv in data[0]["conversations"]:
                        if conv.get("role") == "assistant" and "reasoning" in conv:
                            reas = conv["reasoning"]
                            if "<think>" not in reas:
                                conv["reasoning"] = f"<think>\\n{reas}\\n</think>"
                    with open(out_json_path, 'w', encoding='utf-8') as f:
                        import json
                        json.dump(data, f, indent=4, ensure_ascii=False)
                    log(f"✅ Assembly Success! Saved to {os.path.basename(out_json_path)}")
                    return True
            except Exception as e:
                log(f"⚠️ Direct JSON parsing failed: {e}. Falling back to block extraction...")
        
        # 1. Primary Regex Extraction'''

content = content.replace('''def validate_and_save_json(llm_response, out_json_path, thinking_text=None):
    """Assemble the granular semantic blocks into a valid 6-turn conversational JSON."""
    try:
        import json_repair
        
        # 0. Clean repetition loops first
        llm_response = clean_repetitive_text(llm_response)
        
        # 1. Primary Regex Extraction''', json_extract_patch)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("SUCCESS")
