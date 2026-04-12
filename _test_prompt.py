"""Verify the prompt contains all 17 block delimiters."""
import sys, os
sys.path.insert(0, '.')
from pipeline import build_generation_prompt

variation = (94, 'Critique of the Approach', 'Perception Lead / Senior DevOps Engineer')
prompt = build_generation_prompt(variation, 8, 1, 'test_doc', 'TECHNICAL')

blocks = ['METADATA', 'REASONING', 'TURN-1-USER', 
          'GPF-HEADER', 'GPF-PROBLEM-DEFINITION', 'GPF-ABSTRACTION-LEVEL',
          'GPF-ARCHITECTURE', 'GPF-FORMAL-SPECIFICATION',
          'GPF-EVALUATION', 'GPF-CONSTRAINTS',
          'GPF-CLASSIFICATION', 'GPF-RELATIONAL-NETWORK',
          'GPF-EXEMPLARS', 'GPF-HISTORY',
          'TURN-3-USER', 'TURN-4-ASSISTANT',
          'TURN-5-USER', 'TURN-6-ASSISTANT']

found = 0
for b in blocks:
    marker = f'!!!!!{b}!!!!!'
    if marker in prompt:
        found += 1
    else:
        print(f'MISSING: {marker}')

print(f'Found {found}/17 block delimiters in prompt')
print(f'Prompt length: {len(prompt)} chars')

# Verify no JSON template remnants
if '"conversations"' in prompt:
    print('WARNING: JSON conversations template still present!')
else:
    print('OK: No JSON template remnants')
