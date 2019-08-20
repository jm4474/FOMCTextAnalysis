import pandas as pd
def main():
	df = pd.read_csv("../../../collection/python/output/derived_data.csv")
	df['sizes'] = df['file_size'].apply(real_file_size)
	#print(len(df[df.sizes.isnull()])/len(df))
	print(df[df.sizes.isnull()].groupby('grouping').sum())
	print(str(float(df['sizes'].sum(axis=0))/1000000)+ "GB")
def real_file_size(s):
	s = str(s).lower()
	if not s:
		return
	file_size = s.split()
	if len(file_size)<=1:
		return float(s)
	if file_size[1] == "mb":
		return float(file_size[0])*1000
	elif file_size[1] == "kb":
		return float(file_size[0])
	else:
		print(s)


if __name__ == "__main__":
	main()