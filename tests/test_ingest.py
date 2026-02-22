from src.ingest import load_transactions

df = load_transactions("data/sample.csv")
print(df.head())
print("\nSummary:")
print(df.describe())