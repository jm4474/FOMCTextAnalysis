import csv
def main():
    file = open("../output/Greenbook/1983may.txt").read()

    #Remove unwanted content
    file = file.strip()
    file = file.split("\n",1)[1]
    file = file.rsplit("Append",1)[0]
    file = file.strip()

    lines = file.split("\n")
    years = lines[0].split()
    quarters = lines[1].split()

    data_table = lines[4:]
    data = []
    for row in data_table:
        if len(row.split())<len(quarters):
            continue
        if not row or not row.split():
            continue
        if "]" in row:
            var_and_data = row.split("]", 1)
            macro_variable = var_and_data[0]+"]".strip()
        else:
            var_and_data = row.split("  ", 1)
            macro_variable = var_and_data[0].strip()
        row_data = var_and_data[1].strip().split()
        for column in range(len(quarters)):
            value = {}
            value['year'] = years[column]
            value['quarter'] = quarters[column]
            value['macro_variable'] = macro_variable
            value['number'] = row_data[column]
            data.append(value)
    with open('../output/greenbookmay.csv', mode='w') as csvfile:
        fieldnames = list(data[0].keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for value in data:
            writer.writerow(value)

main()