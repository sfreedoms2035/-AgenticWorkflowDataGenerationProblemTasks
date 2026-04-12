"""Test: verify repair_missing_cot_numbers no longer doubles numbering."""
import sys, json, re
sys.path.insert(0, r'c:\Users\User\VS_Projects\Helpers\Antigravity\AgenticWorkflowPlaywright_Visuals\.agent\scripts')
from auto_repair import repair_missing_cot_numbers

# Test 1: Already numbered (should NOT double)
task1 = {
    "conversations": [{
        "role": "assistant",
        "reasoning": "<think>\n1. Initial Query Analysis & Scoping\n1.1. Deconstruct the Request: The engineering problem...\n2. Assumptions & Context Setting\n</think>"
    }]
}
before = task1["conversations"][0]["reasoning"]
result = repair_missing_cot_numbers(task1)
after = task1["conversations"][0]["reasoning"]
print(f"Test 1 (already numbered): changed={result}")
if "1. 1." in after:
    print(f"  FAIL: Doubled numbering found: {after[:100]}")
else:
    print(f"  PASS: No doubling")

# Test 2: Missing numbers (should add them)
task2 = {
    "conversations": [{
        "role": "assistant",
        "reasoning": "<think>\nInitial Query Analysis & Scoping\nDeconstruct the Request: The engineering problem...\nAssumptions & Context Setting\n</think>"
    }]
}
result2 = repair_missing_cot_numbers(task2)
after2 = task2["conversations"][0]["reasoning"]
print(f"\nTest 2 (missing numbers): changed={result2}")
if "1. Initial Query" in after2:
    print(f"  PASS: Added number prefix")
else:
    print(f"  FAIL: Did not add prefix: {after2[:100]}")

# Test 3: Already doubled (should NOT make it triple)
task3 = {
    "conversations": [{
        "role": "assistant",
        "reasoning": "<think>\n1. 1. Initial Query Analysis & Scoping\n</think>"
    }]
}
result3 = repair_missing_cot_numbers(task3)
after3 = task3["conversations"][0]["reasoning"]
print(f"\nTest 3 (already doubled): changed={result3}")
if "1. 1. 1." in after3:
    print(f"  FAIL: Tripled numbering!")
else:
    print(f"  PASS: Did not add more")
