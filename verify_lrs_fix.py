import pandas as pd

# Verify the LRS fix
excel_file = "lott-excel.xlsx"
df = pd.read_excel(excel_file, sheet_name='lrs_caselevel')

print("=== LRS Routing Fix Verification ===")

# Check lrs_rq_all500 - should be all zeros now
rq_all500_nonzero = (df['lrs_rq_all500'] != 0).sum()
print(f"lrs_rq_all500 non-zero count: {rq_all500_nonzero} (should be 0)")

# Check lrs_lott_framework by routing branch
direct_cases = df[df['lott_routed_branch'] == 'Direct']
rq_cases = df[df['lott_routed_branch'] == 'RQ']

print(f"\nDirect cases with lrs_lott_framework > 0: {(direct_cases['lrs_lott_framework'] > 0).sum()}/{len(direct_cases)}")
print(f"RQ cases with lrs_lott_framework > 0: {(rq_cases['lrs_lott_framework'] > 0).sum()}/{len(rq_cases)}")

# Show sample data to verify the fix
print(f"\nSample cases by routing branch:")
print("Direct cases:")
print(direct_cases[['case_id', 'lott_routed_branch', 'lrs_lott_framework', 'lrs_rq_all500']].head().to_string(index=False))

print("\nRQ cases:")
print(rq_cases[['case_id', 'lott_routed_branch', 'lrs_lott_framework', 'lrs_rq_all500']].head().to_string(index=False))

# Check statistics
print(f"\nLRS Statistics:")
print(f"lrs_lott_framework - avg: {df['lrs_lott_framework'].mean():.2f}, non-zero: {(df['lrs_lott_framework'] > 0).sum()}")
print(f"lrs_rq_all500 - avg: {df['lrs_rq_all500'].mean():.2f}, non-zero: {(df['lrs_rq_all500'] > 0).sum()}")

# Verify fix worked
if rq_all500_nonzero == 0 and (df['lrs_lott_framework'] > 0).sum() == 500:
    print("\n✅ SUCCESS: LRS routing fix worked perfectly!")
    print("- lrs_rq_all500 is now all zeros (no separate second experiment LRS)")
    print("- lrs_lott_framework contains scores for both Direct and RQ routing")
else:
    print("\n❌ Issue found with the fix")
    if rq_all500_nonzero > 0:
        print(f"- lrs_rq_all500 still has {rq_all500_nonzero} non-zero values")
    if (df['lrs_lott_framework'] > 0).sum() != 500:
        print(f"- lrs_lott_framework only has {(df['lrs_lott_framework'] > 0).sum()}/500 non-zero values")