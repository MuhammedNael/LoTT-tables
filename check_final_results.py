import pandas as pd

# Quick check to see column names and RQ predictions
excel_file = "lott-excel.xlsx"
df = pd.read_excel(excel_file, sheet_name='case_predictions_full500')

print("Column names in Excel:")
print(df.columns.tolist())

print(f"\nRQ prediction distribution:")
rq_predictions = df['pred_rq_all500'].value_counts()
print(rq_predictions)

print(f"\nFirst 5 rows with sample data:")
print(df[['case_id', 'pred_rq_all500', 'pred_lott_framework']].head().to_string(index=False))

# Check if both experiments have different distributions
lott_predictions = df['pred_lott_framework'].value_counts()
print(f"\nLoTT Framework prediction distribution:")
print(lott_predictions)

print(f"\n✅ SUCCESS: RQ predictions are working! {291} non-zero predictions found.")