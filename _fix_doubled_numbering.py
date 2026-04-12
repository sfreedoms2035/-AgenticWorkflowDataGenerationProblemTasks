"""Batch fix doubled CoT numbering in existing JSON output files."""
import json, re, os

json_dir = r'c:\Users\User\VS_Projects\Helpers\Antigravity\AgenticWorkflowPlaywright_Visuals\Output\json'
fixed_count = 0
total = 0

for fname in os.listdir(json_dir):
    if not fname.endswith('.json'): continue
    total += 1
    fpath = os.path.join(json_dir, fname)
    try:
        with open(fpath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except:
        continue
    
    if not isinstance(data, list) or not data: continue
    task = data[0]
    changed = False
    
    for conv in task.get('conversations', []):
        if conv.get('role') != 'assistant': continue
        reasoning = conv.get('reasoning', '')
        if not reasoning: continue
        
        # Fix doubled numbering: '1. 1. Title' -> '1. Title'
        new_reasoning = re.sub(r'(\d+\.)\s+\1\s+', r'\1 ', reasoning)
        # Fix doubled sub-numbering: '1.1. 1.1. Title' -> '1.1. Title'
        new_reasoning = re.sub(r'(\d+\.\d+\.)\s+\1\s+', r'\1 ', new_reasoning)
        
        if new_reasoning != reasoning:
            conv['reasoning'] = new_reasoning
            changed = True
    
    if changed:
        with open(fpath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        fixed_count += 1

print(f'Scanned {total} files, fixed {fixed_count} with doubled numbering')
