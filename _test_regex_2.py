import re
import json

with open('test_gpf_task.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Find Turn 1
conv = data[0]['conversations'][1]
reas = conv['reasoning']

m_delim = re.search(r'(?:^|\n)\s*[\*#]*[\\!\[\]]{1,}\s*GPF-PROBLEM-DEFINITION\s*:?\s*[\\!\[\]]{1,}', reas)
if m_delim:
    print('Match Strategy 1:', m_delim.group(), 'at pos:', m_delim.start())
else:
    print('Strategy 1 NO MATCH')

m_header = re.search(r'(?:^|\n)\s*[#\*\\!]*\s*(?:1\.\d*\s+)?(?:Core\s+)?Problem (?:Definition|Statement)', reas, re.IGNORECASE)
if m_header:
    print('Match Strategy 2:', m_header.group(), 'at pos:', m_header.start())

m_think = list(re.finditer(r'[<\\\&]+(?:/|lt;|\\\\)*?think[>\\\&;]+', reas, re.IGNORECASE))
if m_think:
    print('Match Strategy 3:', m_think[-1].group(), 'at pos:', m_think[-1].end())
