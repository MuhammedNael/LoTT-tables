#!/usr/bin/env python3
"""
Populate Excel sheets with case-level predictions and LRS scores
This script fills the blue fields in lott-excel.xlsx as requested by the supervisor
"""

import json
import pandas as pd
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_json_file(file_path: str) -> Any:
    """Load a JSON file safely"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading {file_path}: {e}")
        return None

def load_jsonl_file(file_path: str) -> List[Dict]:
    """Load a JSONL file safely"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return [json.loads(line) for line in f if line.strip()]
    except Exception as e:
        logger.error(f"Error loading {file_path}: {e}")
        return []

def get_case_id_from_filename(filename: str) -> str:
    """Extract case ID from combined_XXXXX.json filename => XXXXX"""
    if filename.startswith('combined_') and filename.endswith('.json'):
        return filename[9:-5]  # Remove 'combined_' and '.json'
    return filename

def convert_case_id_format(case_id: str) -> str:
    """Convert from combined_202316 format to 2023/16 format for baseline matching"""
    if len(case_id) >= 6:
        year = case_id[:4]
        number = case_id[4:]
        return f"{year}/{number}"
    return case_id

def get_ground_truth_label(case_data: Dict) -> str:
    """Extract ground truth label from various possible locations"""
    # First try top-level field (LoTT experiment structure)
    label = case_data.get('ground_truth_label')
    if label is not None:
        return str(label)
    
    # Try inside lott_guided_analysis (RQ experiment structure)
    lott_analysis = case_data.get('lott_guided_analysis', {})
    if lott_analysis and isinstance(lott_analysis, dict):
        nested_label = lott_analysis.get('ground_truth_label')
        if nested_label is not None:
            return str(nested_label)
    
    # Try in decision information (alternative structure)
    decision_info = case_data.get('decision_information', {})
    ground_truth_results = decision_info.get('inceleme_sonuclari_ground_truth', [])
    
    # Look for violation (İhlal) in the ground truth results
    for result in ground_truth_results:
        if result.get('Sonuç') == 'İhlal':
            return '1'
    
    # If no violation found but results exist, assume no violation
    if ground_truth_results:
        return '0'
    
    logger.warning(f"No ground truth label found for case {case_data.get('case_identifier', 'unknown')}")
    return "0"  # Default

def get_framework_prediction(case_data: Dict) -> tuple:
    """Extract framework prediction and routing branch from various possible locations"""
    # First try top-level field (LoTT experiment structure)
    pred = case_data.get('final_prediction_binary')
    processing_status = case_data.get('processing_status', '')
    
    if pred is not None:
        # Determine routing branch from processing status
        if 'Direct' in processing_status:
            branch = "Direct"
        elif 'RQ' in processing_status:
            branch = "RQ"
        else:
            branch = "Direct"  # Default to Direct
        return str(pred), branch
    
    # Try inside lott_guided_analysis (RQ experiment structure)
    lott_analysis = case_data.get('lott_guided_analysis', {})
    if lott_analysis and isinstance(lott_analysis, dict):
        nested_pred = lott_analysis.get('final_prediction_binary')
        nested_status = lott_analysis.get('processing_status', '')
        
        if nested_pred is not None:
            # Determine branch from nested processing status
            if 'Swarm RQ' in nested_status or 'RQ' in nested_status:
                branch = "RQ"
            else:
                branch = "Direct"
            return str(nested_pred), branch
        
        # Fallback: look for İhlal Tespiti (Binary)
        if 'İhlal Tespiti (Binary)' in lott_analysis:
            pred = lott_analysis.get('İhlal Tespiti (Binary)', '0')
            return str(pred), "Direct"
    
    logger.warning(f"No prediction found for case {case_data.get('case_identifier', 'unknown')}")
    return "0", "Unknown"

def extract_baseline_predictions(baseline_data: List[Dict], case_id_baseline_format: str) -> Dict[str, str]:
    """Extract baseline predictions for a specific case"""
    predictions = {}
    
    # Initialize all baseline predictions to "0"
    baseline_methods = [
        'g20_standard', 'g20_cot', 'g20_ls',
        'g25flash_standard', 'g25flash_cot', 'g25flash_ls', 
        'g25pro_standard', 'g25pro_cot', 'g25pro_ls'
    ]
    
    for method in baseline_methods:
        predictions[f'pred_{method}'] = "0"
    
    # Find the case in baseline data
    case_entry = None
    for entry in baseline_data:
        if entry.get('case_identifier') == case_id_baseline_format:
            case_entry = entry
            break
    
    if not case_entry:
        logger.warning(f"No baseline data found for case {case_id_baseline_format}")
        return predictions
    
    # Extract predictions from baseline_evaluations
    baseline_evaluations = case_entry.get('baseline_evaluations', [])
    
    for eval_result in baseline_evaluations:
        model_name = eval_result.get('model_name', '')
        method = eval_result.get('prompting_method', '')
        predicted_binary = eval_result.get('predicted_binary', '0')
        
        # Map to our column naming convention
        method_key = None
        if model_name == 'gemini-2.0-flash':
            if method == 'baseline_direct':
                method_key = 'pred_g20_standard'
            elif method == 'chain_of_thought':
                method_key = 'pred_g20_cot'
            elif method == 'legal_syllogism':
                method_key = 'pred_g20_ls'
        elif model_name == 'gemini-2.5-flash':
            if method == 'baseline_direct':
                method_key = 'pred_g25flash_standard'
            elif method == 'chain_of_thought':
                method_key = 'pred_g25flash_cot'
            elif method == 'legal_syllogism':
                method_key = 'pred_g25flash_ls'
        elif model_name == 'gemini-2.5-pro':
            if method == 'baseline_direct':
                method_key = 'pred_g25pro_standard'
            elif method == 'chain_of_thought':
                method_key = 'pred_g25pro_cot'
            elif method == 'legal_syllogism':
                method_key = 'pred_g25pro_ls'
        
        if method_key:
            predictions[method_key] = str(predicted_binary)
    
    return predictions

def load_rq_experiment_data(rq_results_dir: Path) -> Dict[str, str]:
    """Load RQ experiment predictions"""
    rq_predictions = {}
    
    if not rq_results_dir.exists():
        logger.warning(f"RQ experiment directory not found: {rq_results_dir}")
        return rq_predictions
    
    rq_files = list(rq_results_dir.glob("combined_*.json"))
    logger.info(f"Found {len(rq_files)} RQ experiment files")
    
    for file_path in rq_files:
        case_data = load_json_file(str(file_path))
        if not case_data:
            continue
            
        case_id = get_case_id_from_filename(file_path.name)
        
        # In RQ files, final_prediction_binary is inside lott_guided_analysis
        lott_analysis = case_data.get('lott_guided_analysis', {})
        if lott_analysis and isinstance(lott_analysis, dict):
            final_prediction = lott_analysis.get('final_prediction_binary', '0')
        else:
            # Fallback to top-level (shouldn't happen in RQ files)
            final_prediction = case_data.get('final_prediction_binary', '0')
            
        rq_predictions[case_id] = str(final_prediction)
    
    return rq_predictions

def extract_lrs_scores_and_reasoning_points(lrs_data: Dict, case_id: str) -> tuple:
    """Extract LRS scores and reasoning point count for a case"""
    
    # Initialize default values
    lrs_scores = {}
    reasoning_point_count = 0
    
    # Initialize all LRS scores to 0.0
    lrs_methods = [
        'lrs_lott_framework', 'lrs_rq_all500',
        'lrs_g20_standard', 'lrs_g20_cot', 'lrs_g20_ls',
        'lrs_g25flash_standard', 'lrs_g25flash_cot', 'lrs_g25flash_ls',
        'lrs_g25pro_standard', 'lrs_g25pro_cot', 'lrs_g25pro_ls'
    ]
    
    for method in lrs_methods:
        lrs_scores[method] = 0.0
    
    # Find case in LRS data
    case_results = lrs_data.get('case_results', [])
    case_entry = None
    
    for case in case_results:
        # Try different case identifier formats
        case_identifier = case.get('case_identifier', '')
        if (case_identifier == case_id or 
            case_identifier == f"combined_{case_id}" or
            case_identifier.replace('combined_', '') == case_id):
            case_entry = case
            break
    
    if not case_entry:
        logger.warning(f"No LRS data found for case {case_id}")
        return lrs_scores, reasoning_point_count
    
    # Extract reasoning point count
    reasoning_points = case_entry.get('reasoning_points', [])
    reasoning_point_count = len(reasoning_points)
    
    # Extract LRS scores from the 'scores' field
    scores = case_entry.get('scores', {})
    
    # Map score keys to our column names  
    score_mapping = {
        'baseline_gemini-2.0-flash_standard_direct': 'lrs_g20_standard',
        'baseline_gemini-2.0-flash_chain_of_thought': 'lrs_g20_cot',  # No _direct suffix
        'baseline_gemini-2.0-flash_legal_syllogism': 'lrs_g20_ls',   # No _direct suffix
        'baseline_gemini-2.5-flash_standard_direct': 'lrs_g25flash_standard',
        'baseline_gemini-2.5-flash_chain_of_thought': 'lrs_g25flash_cot',  # No _direct suffix
        'baseline_gemini-2.5-flash_legal_syllogism': 'lrs_g25flash_ls',    # No _direct suffix
        'baseline_gemini-2.5-pro_standard_direct': 'lrs_g25pro_standard',
        'baseline_gemini-2.5-pro_chain_of_thought': 'lrs_g25pro_cot',      # No _direct suffix
        'baseline_gemini-2.5-pro_legal_syllogism': 'lrs_g25pro_ls'         # No _direct suffix
    }
    
    # Handle LoTT Framework LRS (both 'lott_guided' and 'rq' are part of first experiment)
    if 'lott_guided' in scores:
        lott_score = scores['lott_guided'].get('reasoning_score', 0.0)
        if isinstance(lott_score, (int, float)):
            lrs_scores['lrs_lott_framework'] = float(lott_score)
    elif 'rq' in scores:
        rq_score = scores['rq'].get('reasoning_score', 0.0)  
        if isinstance(rq_score, (int, float)):
            lrs_scores['lrs_lott_framework'] = float(rq_score)
    
    # lrs_rq_all500 remains 0.0 (no separate second experiment LRS data)
    
    # Handle baseline LRS scores
    for score_key, lrs_key in score_mapping.items():
        if score_key in scores:
            score_value = scores[score_key].get('reasoning_score', 0.0)
            if isinstance(score_value, (int, float)):
                lrs_scores[lrs_key] = float(score_value)
    
    return lrs_scores, reasoning_point_count

def main():
    """Main function to populate the Excel sheets"""
    
    # Define paths
    base_path = Path(r"c:\Users\Muhammed Nael\OneDrive\Desktop\VSCode_Projects\LoTTTables")
    
    # Input paths  
    combined_results_dir = base_path / "final_results_500_cases" / "combined_processing_results"
    rq_results_dir = base_path / "results_RQ_SWA_Experiment_500" / "combined_processing_results"
    baseline_results_file = base_path / "Baseline_Prompts_Results" / "comparison_results_all.jsonl"
    lrs_results_file = base_path / "final_LRS_500_cases_evaluation_results_477_and_23" / "reasoning_evaluation_results.json"
    excel_file = base_path / "lott-excel.xlsx"
    
    # Check if files exist
    if not combined_results_dir.exists():
        logger.error(f"Combined results directory not found: {combined_results_dir}")
        return
    
    if not rq_results_dir.exists():
        logger.error(f"RQ results directory not found: {rq_results_dir}")
        return
    
    if not baseline_results_file.exists():
        logger.error(f"Baseline results file not found: {baseline_results_file}")
        return
        
    if not lrs_results_file.exists():
        logger.error(f"LRS results file not found: {lrs_results_file}")
        return
        
    if not excel_file.exists():
        logger.error(f"Excel file not found: {excel_file}")
        return
    
    logger.info("Loading data files...")
    
    # Load baseline, LRS, and RQ experiment data
    baseline_data = load_jsonl_file(str(baseline_results_file))
    lrs_data = load_json_file(str(lrs_results_file))
    rq_experiment_predictions = load_rq_experiment_data(rq_results_dir)
    
    if not baseline_data:
        logger.error("Failed to load baseline data")
        return
    
    if not lrs_data:
        logger.error("Failed to load LRS data") 
        return
    
    logger.info(f"Loaded {len(baseline_data)} baseline entries, LRS data, and {len(rq_experiment_predictions)} RQ predictions")
    
    # Process all combined JSON files
    case_predictions_data = []
    lrs_caselevel_data = []
    
    combined_files = list(combined_results_dir.glob("combined_*.json"))
    logger.info(f"Found {len(combined_files)} combined result files")
    
    for file_path in combined_files:
        case_data = load_json_file(str(file_path))
        if not case_data:
            continue
        
        # Extract case ID from filename  
        case_id = get_case_id_from_filename(file_path.name)
        case_id_baseline_format = convert_case_id_format(case_id)
        
        logger.debug(f"Processing case {case_id} (baseline format: {case_id_baseline_format})")
        
        # Extract basic case information
        gold_label = get_ground_truth_label(case_data)
        framework_pred, routing_branch = get_framework_prediction(case_data)
        
        # Extract baseline predictions
        baseline_predictions = extract_baseline_predictions(baseline_data, case_id_baseline_format)
        
        # Extract LRS scores and reasoning points
        lrs_scores, reasoning_point_count = extract_lrs_scores_and_reasoning_points(lrs_data, case_id)
        
        # Get RQ experiment prediction for this case
        rq_prediction = rq_experiment_predictions.get(case_id, "0")
        
        # Prepare case_predictions_full500 row
        case_pred_row = {
            'case_id': case_id,
            'gold_label': gold_label,
            'lott_routed_branch': routing_branch,
            'pred_lott_framework': framework_pred,
            'pred_rq_all500': rq_prediction,
            **baseline_predictions
        }
        
        case_predictions_data.append(case_pred_row)
        
        # Prepare lrs_caselevel row
        lrs_row = {
            'case_id': case_id,
            'num_reason_points': reasoning_point_count,
            'lott_routed_branch': routing_branch,
            **lrs_scores
        }
        
        lrs_caselevel_data.append(lrs_row)
    
    logger.info(f"Processed {len(case_predictions_data)} cases")
    
    # Create DataFrames
    case_predictions_df = pd.DataFrame(case_predictions_data)
    lrs_caselevel_df = pd.DataFrame(lrs_caselevel_data)
    
    logger.info("Writing to Excel file...")
    
    # Load existing Excel file and update specific sheets
    try:
        with pd.ExcelWriter(str(excel_file), mode='a', if_sheet_exists='overlay', engine='openpyxl') as writer:
            # Write case_predictions_full500 sheet (starting from row 2 to preserve headers)
            case_predictions_df.to_excel(writer, sheet_name='case_predictions_full500', 
                                       index=False, header=False, startrow=1)
            
            # Write lrs_caselevel sheet (starting from row 2 to preserve headers)  
            lrs_caselevel_df.to_excel(writer, sheet_name='lrs_caselevel',
                                    index=False, header=False, startrow=1)
            
        logger.info("✅ Successfully updated Excel file!")
        
        # Print summary statistics
        logger.info(f"\nSUMMARY STATISTICS:")
        logger.info(f"Total cases processed: {len(case_predictions_data)}")
        logger.info(f"Gold label distribution: {case_predictions_df['gold_label'].value_counts().to_dict()}")
        logger.info(f"Routing branch distribution: {case_predictions_df['lott_routed_branch'].value_counts().to_dict()}")
        logger.info(f"Average reasoning points: {lrs_caselevel_df['num_reason_points'].mean():.2f}")
        
    except Exception as e:
        logger.error(f"Error writing to Excel file: {e}")
        
        # Fallback: save as new Excel file
        backup_file = base_path / "lott-excel-populated.xlsx" 
        try:
            with pd.ExcelWriter(str(backup_file), engine='openpyxl') as writer:
                case_predictions_df.to_excel(writer, sheet_name='case_predictions_full500', index=False)
                lrs_caselevel_df.to_excel(writer, sheet_name='lrs_caselevel', index=False)
            
            logger.info(f"✅ Saved data to backup file: {backup_file}")
            
        except Exception as backup_error:
            logger.error(f"Failed to save backup file: {backup_error}")

if __name__ == "__main__":
    main()