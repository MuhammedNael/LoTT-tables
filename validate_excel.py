import pandas as pd

print("Validating Excel file population...")
lrs_case = pd.read_excel('lott-excel.xlsx', sheet_name='lrs_caselevel')

print('Sample LRS scores (first 3 cases):')
print(lrs_case[['case_id', 'num_reason_points', 'lrs_lott_framework', 'lrs_rq_all500']].head(3))

print('\nLRS score statistics:')
lrs_cols = ['lrs_lott_framework', 'lrs_rq_all500']
for col in lrs_cols:
    non_zero = (lrs_case[col] != 0.0).sum()
    mean_val = lrs_case[col].mean()
    print(f'{col}: {non_zero} non-zero scores, mean={mean_val:.3f}')

print('\nReasoning points statistics:')
print(f'Min: {lrs_case["num_reason_points"].min()}')
print(f'Max: {lrs_case["num_reason_points"].max()}')
print(f'Mean: {lrs_case["num_reason_points"].mean():.2f}')

print("\n✅ Validation complete!")