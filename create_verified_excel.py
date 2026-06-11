import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
import warnings
warnings.filterwarnings('ignore')

def calculate_metrics(y_true, y_pred):
    """Calculate all required metrics for binary classification"""
    
    # Convert to numpy arrays and ensure binary values
    y_true = np.array(y_true).astype(int)
    y_pred = np.array(y_pred).astype(int)
    
    # Calculate basic metrics
    accuracy = accuracy_score(y_true, y_pred)
    
    # Calculate precision, recall, f1 for both classes
    precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, average=None, zero_division=0)
    
    # Handle case where we don't have both classes
    if len(precision) == 1:
        # Only one class present, pad with zeros
        if y_true[0] == 0:  # Only negative class
            precision = [precision[0], 0.0]
            recall = [recall[0], 0.0]
            f1 = [f1[0], 0.0]
        else:  # Only positive class
            precision = [0.0, precision[0]]
            recall = [0.0, recall[0]]
            f1 = [0.0, f1[0]]
    
    # Macro metrics (average of both classes)
    macro_precision = np.mean(precision)
    macro_recall = np.mean(recall)
    macro_f1 = np.mean(f1)
    
    # Positive class metrics (class 1)
    positive_recall = recall[1] if len(recall) > 1 else recall[0] if y_pred[0] == 1 else 0.0
    positive_f1 = f1[1] if len(f1) > 1 else f1[0] if y_pred[0] == 1 else 0.0
    
    return {
        'Accuracy': accuracy,
        'Macro_Precision': macro_precision,
        'Macro_Recall': macro_recall,
        'Macro_F1': macro_f1,
        'Positive_Recall': positive_recall,
        'Positive_F1': positive_f1
    }

def main():
    # Load the existing Excel file
    excel_file = "lott-excel.xlsx"
    df = pd.read_excel(excel_file, sheet_name='case_predictions_full500')
    lrs_df = pd.read_excel(excel_file, sheet_name='lrs_caselevel')
    
    print("Loading Excel data...")
    print(f"Total cases: {len(df)}")
    print(f"Gold label distribution: {df['gold_label'].value_counts().to_dict()}")
    
    # Identify all prediction columns and corresponding LRS columns
    pred_columns = [col for col in df.columns if col.startswith('pred_')]
    lrs_columns = [col for col in lrs_df.columns if col.startswith('lrs_')]
    
    print(f"\nFound {len(pred_columns)} prediction columns:")
    for col in pred_columns:
        print(f"  {col}")
    
    print(f"\nFound {len(lrs_columns)} LRS columns:")
    for col in lrs_columns:
        print(f"  {col}")
    
    # Calculate metrics for each prediction column
    results = []
    
    for pred_col in pred_columns:
        print(f"\nCalculating metrics for {pred_col}...")
        
        # Get method name without 'pred_' prefix
        method_name = pred_col.replace('pred_', '')
        
        # Get predictions and convert to int
        predictions = df[pred_col].astype(int)
        gold_labels = df['gold_label'].astype(int)
        
        # Calculate performance metrics
        metrics = calculate_metrics(gold_labels, predictions)
        
        # Calculate LRS average if corresponding LRS column exists
        lrs_col = f"lrs_{method_name}"
        lrs_average = 0.0
        
        if lrs_col in lrs_df.columns:
            lrs_values = lrs_df[lrs_col]
            lrs_average = lrs_values.mean()
            print(f"  LRS Average: {lrs_average:.4f}")
        else:
            print(f"  LRS Average: No corresponding LRS column found")
        
        # Create result row
        result_row = {
            'Method': method_name,
            'LRS_Average': round(lrs_average, 4),
            **metrics
        }
        results.append(result_row)
        
        # Print summary
        print(f"  Accuracy: {metrics['Accuracy']:.4f}")
        print(f"  Macro F1: {metrics['Macro_F1']:.4f}")
        print(f"  Positive F1: {metrics['Positive_F1']:.4f}")
    
    # Convert results to DataFrame
    results_df = pd.DataFrame(results)
    
    # Round all numeric columns to 4 decimal places
    numeric_cols = ['LRS_Average', 'Accuracy', 'Macro_Precision', 'Macro_Recall', 'Macro_F1', 'Positive_Recall', 'Positive_F1']
    for col in numeric_cols:
        results_df[col] = results_df[col].round(4)
    
    # Create Excel file with multiple sheets
    output_file = "verified_excel.xlsx"
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Sheet 1: Performance Metrics (with LRS)
        results_df.to_excel(writer, sheet_name='Performance_Metrics', index=False)
        
        # Sheet 2: Original Case Predictions (for reference)
        df.to_excel(writer, sheet_name='Case_Predictions', index=False)
        
        # Sheet 3: LRS Case Level (for reference)
        lrs_df.to_excel(writer, sheet_name='LRS_CaseLevel', index=False)
        
        # Sheet 4: Summary Statistics
        summary_stats = {
            'Metric': ['Total Cases', 'Positive Cases', 'Negative Cases', 
                      'Best Accuracy', 'Best Macro F1', 'Best Positive F1', 'Best LRS Average'],
            'Value': [
                len(df),
                (df['gold_label'] == 1).sum(),
                (df['gold_label'] == 0).sum(),
                f"{results_df['Accuracy'].max():.4f} ({results_df.loc[results_df['Accuracy'].idxmax(), 'Method']})",
                f"{results_df['Macro_F1'].max():.4f} ({results_df.loc[results_df['Macro_F1'].idxmax(), 'Method']})",
                f"{results_df['Positive_F1'].max():.4f} ({results_df.loc[results_df['Positive_F1'].idxmax(), 'Method']})",
                f"{results_df['LRS_Average'].max():.4f} ({results_df.loc[results_df['LRS_Average'].idxmax(), 'Method']})"
            ]
        }
        summary_df = pd.DataFrame(summary_stats)
        summary_df.to_excel(writer, sheet_name='Summary_Stats', index=False)
    
    print(f"\n✅ Successfully created {output_file}")
    print(f"\nSheets created:")
    print(f"  1. Performance_Metrics - Main results with all calculated metrics + LRS averages")
    print(f"  2. Case_Predictions - Original case-level predictions")
    print(f"  3. LRS_CaseLevel - Original LRS scores for each case")
    print(f"  4. Summary_Stats - Overall statistics and best performers")
    
    # Display the performance metrics table
    print(f"\n=== PERFORMANCE METRICS (with LRS) ===")
    print(results_df.to_string(index=False))
    
    # Show best performers
    print(f"\n=== BEST PERFORMERS ===")
    print(f"Best Accuracy: {results_df.loc[results_df['Accuracy'].idxmax(), 'Method']} ({results_df['Accuracy'].max():.4f})")
    print(f"Best Macro F1: {results_df.loc[results_df['Macro_F1'].idxmax(), 'Method']} ({results_df['Macro_F1'].max():.4f})")
    print(f"Best Positive F1: {results_df.loc[results_df['Positive_F1'].idxmax(), 'Method']} ({results_df['Positive_F1'].max():.4f})")
    print(f"Best LRS Average: {results_df.loc[results_df['LRS_Average'].idxmax(), 'Method']} ({results_df['LRS_Average'].max():.4f})")

if __name__ == "__main__":
    main()