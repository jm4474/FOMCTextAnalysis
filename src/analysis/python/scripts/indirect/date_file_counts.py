import pandas as pd
def main():
	df = pd.read_csv("../../../../collection/python/output/derived_data.csv")

	df['date'] = df['end_date']
	df['File Type'] = df['grouping']
	df = df.drop_duplicates(subset=["end_date","File Type"])

	dates = sorted(list(df['date']))

	for date in dates:
		df[date] = df['date']==date

	file_counts = df.groupby('File Type').sum().astype(int)
	file_counts = file_counts[file_counts.columns[1:]]
	file_counts.to_csv("~/Desktop/date_file_counts.csv")

if __name__ == "__main__":
	main()