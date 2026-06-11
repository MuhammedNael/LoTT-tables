import json

# Check the actual structure of LRS data to see what score keys exist
with open('final_LRS_500_cases_evaluation_results_477_and_23/reasoning_evaluation_results.json', 'r', encoding='utf-8') as f:
    lrs_data = json.load(f)

if 'case_results' in lrs_data and len(lrs_data['case_results']) > 0:
    # Get first case to see the structure
    first_case = lrs_data['case_results'][0]
    print("First case structure:")
    print(f"Case identifier: {first_case.get('case_identifier')}")
    
    if 'scores' in first_case:
        print(f"\nActual score keys found:")
        for key in first_case['scores'].keys():
            print(f"  {key}")
            
        # Show a few sample score structures
        print(f"\nSample score structures:")
        for i, (key, score_data) in enumerate(list(first_case['scores'].items())[:3]):
            print(f"\n{key}:")
            if isinstance(score_data, dict):
                for subkey, value in score_data.items():
                    print(f"  {subkey}: {value}")
            else:
                print(f"  {score_data}")
    else:
        print("No 'scores' field found in first case")
        print("Available fields:", list(first_case.keys()))
else:
    print("No case_results found or empty")