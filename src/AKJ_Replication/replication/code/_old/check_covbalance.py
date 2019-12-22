import pandas as pd

df=pd.read_csv("../../data/covbal.csv")

df_mean = df.mean(axis=0)


df_means = pd.DataFrame(df_mean)

df_means["variables"] = df_means.index
df_means["variable"] = df_means["variables"].apply(lambda x: x.split("_")[0])
df_means["policy"] = df_means["variables"].apply(lambda x: x.split("_")[1])
df_means.rename({0:"mean"},axis='columns',inplace=True)
df_means.drop(columns=["variables"],inplace=True)

df_new=df_means.pivot(index='variable', columns='policy', values='mean')
df_new = df_new[["m050","m025","0","025","050"]]

print(df_new.to_latex())


def main():

if __name__ == "__main__":
    main()