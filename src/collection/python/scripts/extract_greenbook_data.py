import pandas
import numpy
import csv
import os
'''
@Author Anand Chitale
This file takes the pre-downloaded greenbook excel data file from the 
philidelphia fed and extracts all economic indicators into a greenbook data csv file
'''
def extract_greenbook_data():
    greenbook_path = "../data/greenbook_excel/"
    all_projections = []
    if os.path.exists(greenbook_path):
        files = [file for file in os.listdir(greenbook_path) if file != ".DS_Store"]
        for filename in files:
            print(filename)
            all_projections.extend(extract_variable_forecasts(greenbook_path+filename))
    write_to_csv(all_projections)

def extract_variable_forecasts(filename):
    projections = []
    df = pandas.read_excel(filename)
    macro_variable = filename.split("greenbook_excel/")[1].split("_",1)[0]

    dates = df["Date"]
    meetings = []
    for column_name in df:
        meetings.append(column_name)
    for meeting in meetings[1:]:
        meeting_date = meeting.split("_")[1]

        for row in range(len(df[meeting])):
            if numpy.isnan(df[meeting][row]):
                continue
            projection = {}
            projection['macro_variable'] = macro_variable
            projection['meeting_date'] = meeting_date
            projection['forecast_date'] = dates[row]
            projection['projection'] = df[meeting][row]
            projections.append(projection)
    return projections

def write_to_csv(projections):
    with open('../output/greenbook_data.csv', 'w') as csvfile:
        fieldnames = projections[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for projection in projections:
            writer.writerow(projection)

if __name__ == "__main__":
    extract_greenbook_data()