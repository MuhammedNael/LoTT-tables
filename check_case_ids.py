import json

# Check case ID formats in LoTT cases file
with open('final_500_cases_evaluation_results_LAST_477_and_23/reasoning_evaluation_results_lott_cases.json', 'r', encoding='utf-8') as f:
    lott_data = json.load(f)
print('LoTT case ID examples:')
for i, case in enumerate(lott_data['case_results'][:3]):
    print(f'  {i+1}: {case["case_identifier"]}')

# Check case ID formats in RQ cases file
with open('final_500_cases_evaluation_results_LAST_477_and_23/reasoning_evaluation_results_rq_cases.json', 'r', encoding='utf-8') as f:
    rq_data = json.load(f)
print('\nRQ case ID examples:')
for i, case in enumerate(rq_data['case_results'][:3]):
    print(f'  {i+1}: {case["case_identifier"]}')

# Check case ID formats in baseline results
with open('Baseline_Prompts_Results/comparison_results_all.jsonl', 'r', encoding='utf-8') as f:
    baseline_lines = []
    for i, line in enumerate(f):
        if i >= 3: break
        if line.strip():
            baseline_lines.append(json.loads(line))

print('\nBaseline case ID examples:')
for i, result in enumerate(baseline_lines):
    print(f'  {i+1}: {result["case_identifier"]}')

print('\nTesting ID transformation (removing slashes):')
test_id = lott_data['case_results'][0]['case_identifier']
print(f'Original: {test_id}')
print(f'No slashes: {test_id.replace("/", "")}')
print(f'Combined format: combined_{test_id.replace("/", "")}')