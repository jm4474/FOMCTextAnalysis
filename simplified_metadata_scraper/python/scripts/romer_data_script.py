import re
import pprint
import csv
def main():
    data_points = []
    lines = open("../output/romer_data.txt","r").readlines()
    lines = lines[100:1419]
    no_page_nums = []
    for line in lines:
        if not line.strip().isdigit():
            no_page_nums.append(line)
    lines = ''.join(no_page_nums)
    date_exp = "(?:\d{1,2}/\d{1,2})(?:-\d{1,2})?(?:-\d{1,2}/\d{1,2})?(?:/\d{2})"
    dates = re.findall(date_exp, lines)
    #FIRST LINE IS NEWLINE
    points = re.split(date_exp,lines)[1:]
    assert(len(dates)==len(points))
    for index in range(len(points)):
        data = {}
        date = dates[index]
        if "-" in date:
            date=date.split("-")[0]+"/"+date.split("-")[1].rsplit("/")[-1]
        data['date'] = date
        effect = points[index].strip().split(". ")[0]
        if "no change" in effect:
            data['prev'] = effect.split(",")[0]
            data['new'] = data['prev']
        else:
            data['prev'] = effect.split("to")[0]
            data['new'] = effect.split("to")[1]
        description = points[index].split(". ",1)[1]
        description = description.strip().replace("\n","")
        data['description'] = description
        #print(description)
        data_points.append(data)
    #pprint.pprint(data_points)
    write_to_csv(data_points)
def write_to_csv(documents):
    with open('../output/romer_data.csv', 'w') as csvfile:
        fieldnames = ['date','prev','new','description']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for document in documents:
            writer.writerow(document)
main()