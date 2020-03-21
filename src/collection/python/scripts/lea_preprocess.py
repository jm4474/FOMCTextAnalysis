import spacy
import os
import re
import csv

preprocessor = spacy.load('en_core_web_sm')

MONTHS = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]

short_months = re.compile("(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec) ?\. ?")

#MONTHS2 = ["jan .", "feb .", "mar .", "apr .", "may .", "jun .", "jul .", "aug .", "sep .", "oct .", "nov .", "dec ."]


def preprocess_longdocs(ftype):
    indir = "../output/{}_raw_text".format(ftype)
    outdir = "../output/{}_preprocessed".format(ftype)
    
    nums2 = re.compile('^[- \d\.,p\*†]+$')
    nums = re.compile('^ ?(\w )+\w?$')
    num = re.compile('^-?\d+[\.,]?\d*[\.,]?\d+$')
    sum_suffix = re.compile('( -?\d+\.?\d*[\w%]?){2,}$')
    num_sep = re.compile('[-\d,\.]+ --- [-\d,\.]+ .*[\d%]$')
    rd  = re.compile('\n\n *recent ?.?d ?evelc?op?me?nts?.? *1?\n.?[\(\n]')
    ir = re.compile('\n(for immediate release)|(for release at \d:\d+).*\n')
    qiv = re.compile('^\(?(\d* ?--)? ?QIV')
    
    for fidx, infile in enumerate(os.listdir(indir)):
        if os.path.isfile(os.path.join(indir, infile)) and not os.path.exists(os.path.join(outdir, infile)):
            print("{}\t{}".format(fidx, infile))
            content = open(os.path.join(indir, infile), 'r').read()
            
            if ftype=="bluebook":
                content = re.split(rd, content.lower())[1]
            elif ftype=="statement":
                content = re.split(ir, content.lower())[-1]
                
            newlines = []
            #content = re.sub(r'-\n\s*', '', content) # remove '-' from words that are split at newlines (very low precision, high recall) not done currently
            for line in content.split('\n'):
                line=line.strip().strip(" *")
                line = re.sub("___+", "", line)
                #print(line)
                if not (len(line) < 3 \
                             or nums2.match(line.strip("*").strip())!= None \
                             or nums.match(line.strip("*").strip())!= None \
                             or (num.match(line.split()[0].strip("*").strip())!= None and  num.match(line.split()[-1].strip("*").strip())!= None)\
                             or line.lower().strip() in MONTHS \
                             or re.search(short_months, line.lower()) \
                             or re.search(sum_suffix, line.lower())\
                             or re.search(num_sep, line.lower()) \
                             or re.search(qiv, line)
                             ):
                    newlines.append(line)
            my_doc = preprocessor(' '.join(newlines))
            sentences = [sent.string.strip() for sent in my_doc.sents]
            for sidx, sentence in enumerate(sentences):
                my_sentence = preprocessor(sentence)
                sentences[sidx] = ['\t'.join([token.text, 
                                   token.lemma_, 
                                   token.pos_, 
                                   token.tag_, 
                                   "{}_{}".format(token.ent_type_,token.ent_iob_) if token.ent_type_!= "" else "",
                                   token.dep_,
                                   str(token.is_stop)]) for token in my_sentence]
            outfile = os.path.join(outdir, infile)
            with open(outfile, 'w+') as of:
                of.write('\n\n'.join(['\n'.join(sentence) for sentence in sentences]))
        else:
            print("{}\t{} -- exists".format(fidx, infile))


def preprocess_news_articles():
    infile = "../data/newsarticles_raw_text/all_news_articles.csv"
    outdir = "../data/newsarticles_raw_text/preprocessed"
    outlet_dict = {"the wall street journal":"wsj", "the new york times":"nyt", "the financial times":"ft"}
    
    cr = re.compile("\n[Cc]ontinue reading the main story\n?")
    ad = re.compile("\n[Aa]dvertisement\n?")
    tm = re.compile("View page in TimesMachine")
    da = re.compile("\n[^\n]+Buy Reprints The New York Times Archives\n")
    
    with open(infile, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='\"')
        header = next(reader, None)
        articles_by_date = {}
        for row in reader:
            date = row[5]
            content = row[3].strip()
            content = re.sub(cr, " ", content)
            content = re.sub(ad, " ", content)
            content = re.sub(tm, " ", content)
            content = re.sub(da, " ", content)
            content = content.replace("\n", " ")
            headline = row[4].strip()
            outlet = outlet_dict[row[6].lower()]
            if date not in articles_by_date:
                articles_by_date[date]={}
            if outlet not in articles_by_date[date]:
                articles_by_date[date][outlet] = []
            articles_by_date[date][outlet].append([headline, content])
        for date in sorted(articles_by_date.keys()):
            for outlet, contents in articles_by_date[date].items():
                if not os.path.exists(os.path.join(outdir, "{}_{}.txt".format(date, outlet))):
                    print("processing {}\t{}".format(date, outlet))
                    with open(os.path.join(outdir, "{}_{}.txt".format(date, outlet)), 'w+') as outfile:
                        for article in contents:
                            headline = preprocessor(article[0])
                            body = preprocessor(article[1])
                            sentences = [sent.string.strip() for sent in body.sents]
                            for sidx, sentence in enumerate(sentences):
                                my_sentence = preprocessor(sentence)
                                sentences[sidx] = ['\t'.join([token.text, 
                                        token.lemma_, 
                                        token.pos_, 
                                        token.tag_, 
                                        "{}_{}".format(token.ent_type_,token.ent_iob_) if token.ent_type_!= "" else "",
                                        token.dep_,
                                        str(token.is_stop)]) for token in my_sentence]
                            headline = ['\t'.join([token.text, 
                                        token.lemma_, 
                                        token.pos_, 
                                        token.tag_, 
                                        "{}_{}".format(token.ent_type_,token.ent_iob_) if token.ent_type_!= "" else "",
                                        token.dep_,
                                        str(token.is_stop)]) for token in headline]
                            outfile.write('\n'.join([word for word in headline])+"\n\n<END_OF_HEADLINE>\n\n")
                            outfile.write('\n\n'.join(['\n'.join(sentence) for sentence in sentences]))
                            outfile.write("\n\n<END_OF_ARTICLE>\n\n")
                else:
                    print("{}\t{} -- exists".format(date, outlet))
        
            
def bluebooks_onefile():
    indir = "../output/bluebook_preprocessed"
    outfilename = "all_bluebooks.out"
    with open(os.path.join(indir, outfilename), 'w+') as outfile:
        for infile in os.listdir(indir):
            print(infile)
            if os.path.isfile(os.path.join(indir, infile)) and infile.endswith(".txt"):
                with open(os.path.join(indir, infile), 'r') as this_file:
                    outfile.write('{}\n'.format(infile))
                    for line in this_file.readlines():
                        if len(line.split('\t')) ==7:
                            outfile.write('{} '.format(line.split('\t')[1]))
                        else:
                            outfile.write('\n')
                    outfile.write('\n')

    
    
    
def main():
    preprocess_longdocs("bluebook")#statement
    #preprocess_news_articles()
    #bluebooks_onefile()
    
    
    
if __name__== "__main__":
  main()
