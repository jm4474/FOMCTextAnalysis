import os
import re
import csv
#TODO:
#Unicode Characters of Percent
#Restrictive Regex in Alternative Characterizer
#Uncertain: Header Alternative Approach
#Worth To Veck
#Tword 2 VEC
#Bags of words
def main():
    base = "../output/clean_bluebook/"
    filenames = os.listdir(base)
    results = []
    for filename in filenames:
        results.append(get_alternatives(base+filename))
    write_to_csv(results)

def get_alternatives(filename):
    text = open(filename, 'r').read().strip()
    sentences = text.split(".")
    alternative_mentions=[]
    for sentence in sentences:
        sentence = sentence.replace("\n-", "").replace("\n", " ")
        alternative_match = re.search("([Aa]lternatives?\s*[ABCDEabcde])([^a-zA-Z]|$)",sentence)
        if alternative_match:
            alternative_mentions.append(sentence)

    bluebook = {
        'date': filename.split(".txt")[0].rsplit("/")[-1],
        'num_sentences': len(alternative_mentions),
        'all_sentences': "\n".join(alternative_mentions)
    }
    alternatives = ["alternative a","alternative b", "alternative c", "alternative d", "alternative e"]
    for alternative in alternatives:
        bluebook[alternative.replace(" ","_")] = []
        bluebook['num_'+alternative.replace(" ","_")] = 0
    for sentence in alternative_mentions:
        for alternative in alternatives:
            if ''.join(alternative.split()) in ''.join(sentence.lower().split()):
                bluebook["num_"+alternative.replace(" ","_")] += 1
                bluebook[alternative.replace(" ","_")].append(sentence)
    return bluebook

def write_to_csv(results):
    with open('../output/period_results_clean.csv', 'w') as csvfile:
        fieldnames = results[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow(result)
main()