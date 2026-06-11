import json
from pathlib import Path

# Test reading one file from each experiment
lott_file = Path('final_results_500_cases/combined_processing_results/combined_202316.json')
rq_file = Path('results_RQ_SWA_Experiment_500/combined_processing_results/combined_202316.json')

print('Testing LoTT experiment file:')
with open(lott_file, 'r', encoding='utf-8') as f:
    lott_data = json.load(f)
print(f'Ground truth: {lott_data.get("ground_truth_label")}')
print(f'Prediction: {lott_data.get("final_prediction_binary")}')
print(f'Processing status: {lott_data.get("processing_status")}')

print('\nTesting RQ experiment file:')
with open(rq_file, 'r', encoding='utf-8') as f:
    rq_data = json.load(f)
print(f'Ground truth: {rq_data.get("ground_truth_label")}')  
print(f'Prediction: {rq_data.get("final_prediction_binary")}')
print(f'Processing status: {rq_data.get("processing_status")}')