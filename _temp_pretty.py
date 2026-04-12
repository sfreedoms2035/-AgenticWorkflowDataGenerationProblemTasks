import json
with open('test.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
with open('test_pretty.txt', 'w', encoding='utf-8') as out:
    json.dump(data, out, indent=2)
