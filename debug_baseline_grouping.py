import json
import numpy as np

# Paths
LOTT_CASES_PATH = r"final_500_cases_evaluation_results_LAST_477_and_23\reasoning_evaluation_results_lott_cases.json"
RQ_CASES_PATH = r"final_500_cases_evaluation_results_LAST_477_and_23\reasoning_evaluation_results_rq_cases.json"
BASELINE_RESULTS_PATH = r"Baseline_Prompts_Results\comparison_results_all.jsonl"

def get_direct_lott_case_ids():
    with open(LOTT_CASES_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return set(case['case_identifier'] for case in data['case_results'])

def calculate_baseline_metrics_for_cases(case_ids, baseline_file):
    print(f"Debug: Calculating baseline metrics for {len(case_ids)} cases...")
    
    # Load baseline results
    baseline_results = []
    with open(baseline_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                baseline_results.append(json.loads(line))
    
    # Filter by case_ids with ID transformation
    filtered_results = []
    for result in baseline_results:
        baseline_id = result['case_identifier']
        transformed_id = f"combined_{baseline_id.replace('/', '')}"
        if transformed_id in case_ids:
            filtered_results.append(result)
    
    print(f"Debug: Filtered to {len(filtered_results)} results")
    
    # Group by model + prompting_method and calculate metrics
    method_results = {}
    
    for result in filtered_results:
        for evaluation in result.get('baseline_evaluations', []):
            model_name = evaluation['model_name']
            prompting_method = evaluation['prompting_method']
            predicted_binary = evaluation['predicted_binary']
            ground_truth_label = evaluation['ground_truth_label']
            
            key = f"{model_name}_{prompting_method}"
            
            if key not in method_results:
                method_results[key] = {
                    'predictions': [],
                    'ground_truth': []
                }
            
            method_results[key]['predictions'].append(int(predicted_binary))
            method_results[key]['ground_truth'].append(int(ground_truth_label))
    
    print(f"Debug: Found method combinations: {list(method_results.keys())}")
    
    # Calculate metrics for each method combination
    baseline_metrics = {}
    
    for key, data in method_results.items():
        predictions = np.array(data['predictions'])
        ground_truth = np.array(data['ground_truth'])
        
        # Calculate basic metrics
        accuracy = np.mean(predictions == ground_truth)
        
        # Parse key to get method and model information
        parts = key.split('_')
        model_name = parts[0] + '-' + parts[1]  # e.g., "gemini-2.0"
        method_name = '_'.join(parts[2:])  # e.g., "baseline_direct"
        
        # Clean up method name
        clean_method = method_name.replace('baseline_', '')
        
        method_map = {
            'direct': 'Standard',
            'chain_of_thought': 'CoT',
            'legal_syllogism': 'Legal Syllogism'
        }
        display_method = method_map.get(clean_method, clean_method)
        display_model = model_name.replace('gemini-', 'Gemini ')
        
        baseline_metrics[key] = {
            'method': display_method,
            'model': display_model,
            'accuracy': accuracy,
            'macro_f1': 0.600,  # Simplified for debugging
            'positive_f1': 0.500,  # Simplified for debugging
        }
        
        print(f"Debug: {display_model} - {display_method}: accuracy={accuracy:.3f}")
    
    return baseline_metrics

# Test the function
print("Testing baseline calculation for Direct LoTT...")
direct_case_ids = get_direct_lott_case_ids()
lott_baseline_metrics = calculate_baseline_metrics_for_cases(direct_case_ids, BASELINE_RESULTS_PATH)

# Group by model
models_dict = {}
for key, baseline in lott_baseline_metrics.items():
    model = baseline['model'].replace('Gemini ', '')
    if model not in models_dict:
        models_dict[model] = []
    models_dict[model].append((key, baseline))

print(f"\nGrouped by model:")
for model, methods in models_dict.items():
    print(f"  {model}: {len(methods)} methods")
    for key, baseline in methods:
        print(f"    {baseline['method']}")