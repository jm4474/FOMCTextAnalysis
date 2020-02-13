import os
import pandas as pd

def main():
    
    data_file_name = "../data/derived_data.csv"
    dirs = ["../data/newsarticles_raw_text/preprocessed/"] #"../data/transcript_raw_text/", "../data/minutes_raw_text/", "../data/statement_raw_text/", "../data/bluebook_raw_text/", "../data/agenda_raw_text/", 
    flists = [[w.split('.')[0] for w in os.listdir(d)] for d in dirs]
    datelist = [w.split('_')[0]  for d in dirs for w in os.listdir(d)] # for newstext
    print(flists)
    start_year = 1965
    end_year = 2013
    df = pd.read_csv(data_file_name)
    files = []
    done = {}
    for index, row in df.iterrows():
        startyear = row['start_date']
        endyear = row['end_date']
        if startyear != endyear and startyear not in done:
            for idx, flist in enumerate(flists):
                for fname in flist:
                    if fname.startswith(endyear):
                        if not startyear in datelist:
                #if endyear in flist:
                    #if not startyear in flist:
                            print("renaming {} in {} -- {}".format(endyear, dirs[idx], fname))
                            os.rename("{}{}_{}.txt".format(dirs[idx],endyear,fname.split("_")[1]), "{}{}_{}.txt".format(dirs[idx],startyear,fname.split("_")[1])) # for newstext 
                            #os.rename("{}preprocessed/{}.txt".format(dirs[idx],endyear), "{}preprocessed/{}.txt".format(dirs[idx],startyear))
        done[startyear]=1




if __name__ == "__main__":
    main()
