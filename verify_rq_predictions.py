import json
import pandas as pd

# Quick check to see if RQ predictions are now working
excel_file = "lott-excel.xlsx"

# Read the Excel file
df = pd.read_excel(excel_file, sheet_name='case_predictions_full500')

# Check RQ predictions
rq_predictions = df['pred_rq_all500'].value_counts()
print("RQ prediction distribution:")
print(rq_predictions)
print(f"\nTotal non-zero RQ predictions: {sum(rq_predictions) - rq_predictions.get(0, 0)}")

# Show a few sample rows with RQ predictions = 1
rq_positive_samples = df[df['pred_rq_all500'] == 1].head()
if len(rq_positive_samples) > 0:
    print(f"\nSample cases with RQ prediction = 1:")
    print(rq_positive_samples[['case_id', 'pred_rq_all500', 'pred_lott_framework', 'routing_branch']].to_string(index=False))
else:
    print("\nNo cases found with RQ prediction = 1")

# Show a few sample rows with different routing branches
print(f"\nSample cases by routing branch:")
for branch in ['Direct', 'RQ']:
    branch_samples = df[df['routing_branch'] == branch].head(3)
    if len(branch_samples) > 0:
        print(f"\n{branch} branch samples:")
        print(branch_samples[['case_id', 'pred_rq_all500', 'pred_lott_framework', 'routing_branch']].to_string(index=False))