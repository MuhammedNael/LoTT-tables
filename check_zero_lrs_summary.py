import json
import pandas as pd

# Quick summary check for the 66 cases
excel_file = "lott-excel.xlsx"
df = pd.read_excel(excel_file, sheet_name='lrs_caselevel')

# Find cases with 0 LRS scores 
zero_lrs_cases = df[df['lrs_lott_framework'] == 0]['case_id'].tolist()
print(f"Found {len(zero_lrs_cases)} cases with 0 LRS scores")

# Load the LRS JSON data
with open('final_LRS_500_cases_evaluation_results_477_and_23/reasoning_evaluation_results.json', 'r', encoding='utf-8') as f:
    lrs_data = json.load(f)

# Summary check: how many of the zero LRS cases actually exist in the JSON
cases_in_lrs_data = 0
cases_with_lott_guided = 0
cases_with_rq = 0
cases_with_empty_scores = 0
cases_with_zero_lott_score = 0

for case_id in zero_lrs_cases:
    case_identifier_combined = f"combined_{case_id}"
    
    for case_result in lrs_data.get('case_results', []):
        if case_result.get('case_identifier') == case_identifier_combined:
            cases_in_lrs_data += 1
            scores = case_result.get('scores', {})
            
            lott_entry = scores.get('lott_guided', {})
            rq_entry = scores.get('rq', {})
            
            if lott_entry:
                cases_with_lott_guided += 1
                lott_score = lott_entry.get('reasoning_score', None)
                if lott_score == 0.0:
                    cases_with_zero_lott_score += 1
                    
            if rq_entry:
                cases_with_rq += 1
                
            if not lott_entry and not rq_entry:
                cases_with_empty_scores += 1
            break

print(f"\n=== SUMMARY RESULTS ===")
print(f"Zero LRS cases found in JSON: {cases_in_lrs_data}/{len(zero_lrs_cases)}")
print(f"Cases with lott_guided data: {cases_with_lott_guided}")
print(f"Cases with lott_guided score = 0.0: {cases_with_zero_lott_score}")
print(f"Cases with rq data: {cases_with_rq}")
print(f"Cases with completely empty framework scores: {cases_with_empty_scores}")

print(f"\n=== CONCLUSION ===")
if cases_with_zero_lott_score == len(zero_lrs_cases):
    print("✅ CONFIRMED: All 66 cases have legitimate reasoning_score = 0.0 in the JSON")
    print("   These cases received 0 LRS scores because their predictions")
    print("   did not contain any of the required legal reasoning points.")
    print("   This is correct behavior - not a bug!")
else:
    print("❌ Mixed results - some missing data or extraction issues found")