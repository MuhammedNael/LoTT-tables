import json

# Check the correct evaluation results file
try:
    with open('final_500_cases_evaluation_results_LAST_477_and_23/reasoning_evaluation_results.json', 'r', encoding='utf-8') as f:
        eval_data = json.load(f)
    
    print('Keys in reasoning_evaluation_results.json:')
    for key in eval_data.keys():
        print(f'  {key}')
    
    # Check if this has the agentic metrics we need
    if 'agentic_lott_relevant_direct_relationship_mode' in eval_data:
        direct_metrics = eval_data['agentic_lott_relevant_direct_relationship_mode']
        print(f'\nDirect LoTT accuracy: {direct_metrics.get("overall_performance", {}).get("accuracy", "NOT_FOUND")}')
    
    if 'agentic_rq_path' in eval_data:
        rq_metrics = eval_data['agentic_rq_path'] 
        print(f'RQ accuracy: {rq_metrics.get("overall_performance", {}).get("accuracy", "NOT_FOUND")}')
        
    # Also check the baseline file the script is currently using
    print('\n' + '='*50)
    print('Checking baseline evaluation metrics file:')
    with open('Baseline_Prompts_Results/evaluation_metrics_summary.json', 'r', encoding='utf-8') as f:
        baseline_eval = json.load(f)
    
    print('Keys in baseline evaluation_metrics_summary.json:')
    for key in list(baseline_eval.keys())[:10]:  # Show first 10 keys
        print(f'  {key}')
    
    # Check if baseline file has agentic metrics
    if 'agentic_lott_relevant_direct_relationship_mode' in baseline_eval:
        print('Found agentic metrics in baseline file')
        direct_baseline = baseline_eval['agentic_lott_relevant_direct_relationship_mode']
        print(f'Direct LoTT accuracy: {direct_baseline.get("overall_performance", {}).get("accuracy", "NOT_FOUND")}')
    else:
        print('No agentic metrics found in baseline file')
        
except Exception as e:
    print(f'Error: {e}')