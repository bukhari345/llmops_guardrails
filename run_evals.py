# run_evals.py - give the RAG assistant a fixed exam (evals.json) and score it
#
# Usage: python run_evals.py                          -> tests prompts/rag_v2.txt
#        python run_evals.py prompts/rag_broken.txt   -> tests another prompt
 
import json
import sys
 
from rag import ask
 
PASS_MARK = 0.8   # at least 80% of questions must pass
prompt_file = sys.argv[1] if len(sys.argv) > 1 else "prompts/rag_v2.txt"
cases = json.load(open("evals.json", encoding="utf-8"))
 
 
def normalise(text):
    # lower case, and turn curly apostrophes (don’t) into straight ones (don't)
    return text.lower().replace("\u2019", "'")
 
 
print(f"Testing {prompt_file} with {len(cases)} questions\n")
passed = 0
for number, case in enumerate(cases, start=1):
    result = ask(case["question"], prompt_file)
 
    # Check 1: does the answer contain the key fact (or "I don't know")?
    answer_ok = normalise(case["must_contain"]) in normalise(result["answer"])
    # Check 2: did the search find the right document? (skipped when "source" is empty)
    source_ok = not case["source"] or case["source"] in result["sources"]
 
    ok = answer_ok and source_ok
    passed += ok
    print(f"Q{number} {'PASS' if ok else 'FAIL'}  {case['question'][:45]:45}  "
          f"answer: {'ok' if answer_ok else 'WRONG'}  search: {'ok' if source_ok else 'WRONG'}")
    if not ok:
        print(f"      got: {result['answer'][:100]}")
 
score = passed / len(cases)
print(f"\nScore: {passed}/{len(cases)} = {score:.0%}   (pass mark {PASS_MARK:.0%})")
 
if score < PASS_MARK:
    print("EVAL GATE: FAILED - this change must not be released")
    sys.exit(1)
print("EVAL GATE: PASSED")
