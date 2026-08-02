import pandas as pd

# List of CSV files in the order you want to merge
files = [
    "nifty17-20.csv",
    "nifty20-22.csv",
    "nifty23-25.csv",
    "nifty25-till.csv"
]

# Read and combine all files
df = pd.concat([pd.read_csv(file) for file in files], ignore_index=True)

# Save merged file
output_file = "../../data/nifty/Nifty_Weekly_2017_to_july_2026.csv"
df.to_csv(output_file, index=False)

print(f"Merged successfully! Total rows: {len(df)}")
print(f"Saved as: {output_file}")