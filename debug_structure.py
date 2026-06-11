import json

# Check the structure of the reasoning evaluation results
with open('final_500_cases_evaluation_results_LAST_477_and_23/reasoning_evaluation_results.json', 'r', encoding='utf-8') as f:
    eval_data = json.load(f)

print('Structure of reasoning_evaluation_results.json:')
print(f'Mode: {eval_data.get("mode", "NOT_FOUND")}')
print(f'Configuration: {eval_data.get("configuration", {})}')

if 'aggregate_stats' in eval_data:
    print('\nAggregate stats keys:')
    agg_stats = eval_data['aggregate_stats']
    for key in agg_stats.keys():
        print(f'  {key}')
        
    # Check if LoTT Framework metrics are in aggregate_stats
    if 'agentic_lott_relevant_direct_relationship_mode' in agg_stats:
        direct_metrics = agg_stats['agentic_lott_relevant_direct_relationship_mode']
        print(f'\nDirect LoTT metrics found:')
        print(f'  Overall performance: {direct_metrics.get("overall_performance", {})}')
        
    if 'agentic_rq_path' in agg_stats:
        rq_metrics = agg_stats['agentic_rq_path'] 
        print(f'\nRQ metrics found:')
        print(f'  Overall performance: {rq_metrics.get("overall_performance", {})}')

if 'case_results' in eval_data:
    print(f'\nNumber of case results: {len(eval_data["case_results"])}')
    if len(eval_data['case_results']) > 0:
        print('First case result keys:', list(eval_data['case_results'][0].keys()))