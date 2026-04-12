from run_gemini_playwright_v2 import validate_and_save_json
import os

text = """!!!!!METADATA!!!!!

```json
{
  "training_data_id": "TD-CODING-001749839-T5t2-20260407-v1.0",
  "prompt_version": "CodingTasks_v1.0",
  "model_used_generation": "Gemini-3.1-pro",
  "knowledge_source_date": "2024-06-01",
  "document": "001749839",
  "task_type": "coding_task",
  "affected_role": "Senior Integration Engineer",
  "date_of_generation": "2026-04-07",
  "key_words": ["ASIL-D"],
  "summary": "ASIL-D compliant Fallback Risk Minimization",
  "difficulty": "91",
  "evaluation_criteria": ["Strict adherence"]
}
```

!!!!!REASONING!!!!!
1. Initial Query
Text

!!!!!TURN-1-USER!!!!!
Hi

!!!!!REQUIREMENTS!!!!!
Req 1

!!!!!ARCHITECTURE!!!!!
Arch

!!!!!CODE!!!!!
Code

!!!!!USAGE-EXAMPLES!!!!!
Usage

!!!!!DOCUMENTATION!!!!!
Doc

!!!!!TEST-CRITERIA!!!!!
Test

!!!!!TURN-3-USER!!!!!
[No Thinking] Hi again

!!!!!TURN-4-ASSISTANT!!!!!
<think></think>
Ans 2

!!!!!TURN-5-USER!!!!!
[No Thinking] Hi 3

!!!!!TURN-6-ASSISTANT!!!!!
<think></think>
Ans 3
"""

validate_and_save_json(text, "test.json")
with open("test.json", "r", encoding="utf-8") as f:
    print(f.read())
os.remove("test.json")
