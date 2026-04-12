import re

text = r"""
\!\!\!\!\!GPF-PROBLEM-DEFINITION\!\!\!\!\!
1.1 Problem Statement (Narrative): 

\!\!\!\!\!GPF-ABSTRACTION-LEVEL\!\!\!\!\!
2.1 Description:

<sysml:Package>
<sysml:Block name="DSSAD_Hardware_Architecture">
</sysml:Package>

\!\!\!\!\!GPF-FORMAL-SPECIFICATION\!\!\!\!\!
4.1 Symbolic Representation:

\!\!\!\!\!GPF-EVALUATION\!\!\!\!\!
5.1 Success Metrics:
"""

pattern = r'(?:^|\n)[ \t]*[\*#]*[\\!\[\]]{1,}\s*([A-Z0-9\-_]+)\s*:?\s*[\\!\[\]]{1,}[\*#]*\s*(.*?)(?=(?:^|\n)[ \t]*[\*#]*[\\!\[\]]{1,}\s*[A-Z0-9\-_]+\s*:?\s*[\\!\[\]]{1,}[\*#]*|\s*$)'
matches = re.finditer(pattern, text, re.DOTALL)
blocks = {}
for m in matches:
    n = m.group(1).upper()
    print('Found tag:', n)
    if 'GPF' in n: blocks[n] = m.group(2).strip()
print('Number of valid blocks:', len(blocks))
