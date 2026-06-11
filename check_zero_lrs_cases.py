import json
import pandas as pd

# Check the actual LRS data for cases with 0 scores
excel_file = "lott-excel.xlsx"
df = pd.read_excel(excel_file, sheet_name='lrs_caselevel')

# Find cases with 0 LRS scores 
zero_lrs_cases = df[df['lrs_lott_framework'] == 0]['case_id'].tolist()
print(f"Found {len(zero_lrs_cases)} cases with 0 LRS scores")

# Load the LRS JSON data
with open('final_LRS_500_cases_evaluation_results_477_and_23/reasoning_evaluation_results.json', 'r', encoding='utf-8') as f:
    lrs_data = json.load(f)

print(f"\nChecking first 10 cases with 0 LRS scores:")

for i, case_id in enumerate(zero_lrs_cases[:10]):
    case_identifier_combined = f"combined_{case_id}"
    print(f"\n--- Case {i+1}: {case_id} ---")
    
    # Find this case in LRS data
    case_found = False
    for case_result in lrs_data.get('case_results', []):
        if case_result.get('case_identifier') == case_identifier_combined:
            case_found = True
            scores = case_result.get('scores', {})
            
            # Check if lott_guided or rq scores exist
            lott_score = scores.get('lott_guided', {})
            rq_score = scores.get('rq', {})
            
            print(f"  Case found in LRS data: Yes")
            print(f"  lott_guided entry: {lott_score}")
            print(f"  rq entry: {rq_score}")
            
            if lott_score:
                print(f"    lott_guided reasoning_score: {lott_score.get('reasoning_score', 'NOT FOUND')}")
            if rq_score:
                print(f"    rq reasoning_score: {rq_score.get('reasoning_score', 'NOT FOUND')}")
            
            # Check baseline scores too
            baseline_count = 0
            for key in scores:
                if key.startswith('baseline_'):
                    baseline_entry = scores[key]
                    if baseline_entry and 'reasoning_score' in baseline_entry:
                        baseline_count += 1
            print(f"  Baseline scores with data: {baseline_count}")
            break
    
    if not case_found:
        print(f"  Case found in LRS data: NO")

# Summary check: how many of the zero LRS cases actually exist in the JSON
print(f"\n=== SUMMARY CHECK ===")
cases_in_lrs_data = 0
cases_with_lott_guided = 0
cases_with_rq = 0
cases_with_empty_scores = 0

for case_id in zero_lrs_cases:
    case_identifier_combined = f"combined_{case_id}"
    
    for case_result in lrs_data.get('case_results', []):
        if case_result.get('case_identifier') == case_identifier_combined:
            cases_in_lrs_data += 1
            scores = case_result.get('scores', {})
            
            if 'lott_guided' in scores and scores['lott_guided']:
                cases_with_lott_guided += 1
            if 'rq' in scores and scores['rq']:
                cases_with_rq += 1
            if not any(scores.get(key, {}) for key in ['lott_guided', 'rq']):
                cases_with_empty_scores += 1
            break

print(f"Zero LRS cases found in JSON: {cases_in_lrs_data}/{len(zero_lrs_cases)}")
print(f"Cases with lott_guided data: {cases_with_lott_guided}")
print(f"Cases with rq data: {cases_with_rq}")
print(f"Cases with completely empty framework scores: {cases_with_empty_scores}")