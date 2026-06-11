import pandas as pd

# Check if LRS scores are now working
excel_file = "lott-excel.xlsx"
df = pd.read_excel(excel_file, sheet_name='lrs_caselevel')

# Check the LRS columns that were previously all zeros
lrs_columns = ['lrs_g20_cot', 'lrs_g20_ls', 'lrs_g25flash_cot', 'lrs_g25flash_ls']

print("LRS Score Analysis:")
for col in lrs_columns:
    if col in df.columns:
        non_zero_count = (df[col] != 0).sum()
        avg_score = df[col].mean()
        max_score = df[col].max()
        print(f"{col}: {non_zero_count}/{len(df)} non-zero, avg={avg_score:.2f}, max={max_score:.2f}")
    else:
        print(f"{col}: Column not found")

# Show sample data for verification
print(f"\nSample LRS scores:")
sample_df = df[['case_id'] + lrs_columns].head()
print(sample_df.to_string(index=False))

# Show distribution of one column to verify
if 'lrs_g20_cot' in df.columns:
    print(f"\nDistribution of lrs_g20_cot:")
    print(df['lrs_g20_cot'].describe())
    
    # Show some non-zero values if they exist
    non_zero_lrs = df[df['lrs_g20_cot'] > 0]
    if len(non_zero_lrs) > 0:
        print(f"\nSample non-zero lrs_g20_cot values:")
        print(non_zero_lrs[['case_id', 'lrs_g20_cot']].head().to_string(index=False))
    else:
        print("All lrs_g20_cot values are still zero!")