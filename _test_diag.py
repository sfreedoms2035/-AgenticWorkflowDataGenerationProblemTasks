import json, sys, os
sys.path.insert(0, '.')
from run_gemini_playwright_v2 import validate_and_save_json, extract_semantic_blocks, heuristic_extract_blocks

with open(r'Output\json\1._차량융합신기술분야_Turn2_Task1_raw_fail.txt', 'r', encoding='utf-8') as f:
    raw = f.read()

temp_out = os.path.join('Output', 'json', '_test_output.json')
if os.path.exists(temp_out):
    os.remove(temp_out)

result = validate_and_save_json(raw, temp_out)
print(f"Result: {result}")

if os.path.exists(temp_out):
    with open(temp_out, 'r', encoding='utf-8') as f:
        data = json.load(f)
    item = data[0]
    
    print("\n--- Testing Turn 1 Content Structure ---")
    convs = item.get('conversations', [])
    if len(convs) > 1:
        c = convs[1].get('content', '')
        if isinstance(c, str):
            try:
                j = json.loads(c)
                print(f"Parsed as JSON dict with {len(j.keys())} keys: {list(j.keys())}")
                for k, v in j.items():
                    print(f"  {k}: {len(v)} chars")
            except:
                print("Content is PLAIN TEXT:")
                print(c[:500] + "\n...")
os.remove(temp_out)
