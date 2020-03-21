import os
import re 
import ast

full_alt = re.compile(r'(\( ?\d+ ?\))? *alternative [abcd] ?[.,]*')

def get_alternatives_corpus(fname, outdir=""):
    print("\n", fname)
    content = open(fname).read().strip()
    alts = {'a':[], 'b':[], 'c':[], 'd':[]}
    for paragraph in content.split("\n\n"):
        dist = ast.literal_eval(paragraph.split("\n")[0].strip())
        text = paragraph.split("\n")[1:]
        for alt in [['a', 'b', 'c', 'd'], ['b', 'a', 'c', 'd'], ['c', 'b', 'a', 'd'], ['d', 'a', 'b', 'c']]:
            if dist[alt[0]]>0 and (dist[alt[1]]==dist[alt[2]]==dist[alt[3]]==0 and len(dist['two'])==0):
                pid="-1"
                for idx, sent in enumerate(text):
                    if idx==0:
                        pid=sent.split(")")[0].strip(" ()")
                        sent = ' '.join(sent.split(")")[1:]).strip()
                    if len(sent)>10 and not full_alt.match(sent):
                        alts[alt[0]].append(' '.join([alt[0], 'PAR', pid, sent]))
            else:
                alt_sents = [' '.join([alt[0], 'SENT', '--', sent]) for sent in text if 'alternative {} '.format(alt[0]) in sent and not ' {} '.format(alt[1]) in sent and not ' {} '.format(alt[2]) in sent and not ' {} '.format(alt[3]) in sent and not full_alt.match(sent)]
                if len(alt_sents) > 0 :
                    alts[alt[0]].extend(alt_sents)
    with open(os.path.join(outdir, fname.split('/')[-1]), 'w+') as of:
        for k in sorted(alts.keys()):
            #of.write('{}\n'.format(k))
            for p in alts[k]:
                of.write('{}\n'.format(p))
            of.write('\n')
        
   
def main():
    indir = "/home/lea/academic/melbourne/research/fed_causal/data/bluebook_raw_text/paragraphs_dist2"
    outdir = "/home/lea/academic/melbourne/research/fed_causal/data/bluebook_raw_text/alternative_corpora_withd"
    infiles = os.listdir(indir)
    for f in infiles:
        if f.endswith(".txt"):# and 1987<=int(f.split('-')[0])<=2009:
            get_alternatives_corpus(os.path.join(indir, f), outdir)
    
    
    
    

if __name__== "__main__":
    main()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
#table1 = "Table 1: Alternative Language"
#types = ["Policy", "Decision", "Rationale", "Assessment", "of Risk"]

    
#def read_bluebook(fname):
    #content = open(fname).read()
    #alt_texts = {}
    #for sentence in content.split("\n\n"):
        #words = " ".join([w.split("\t")[0] for w in sentence.split("\n")])
        #any_m = ' '.join(set(alternatives.findall(words)))
        #if len(any_m)>=1:
            #if any_m not in alt_texts:
                #alt_texts[any_m]=[]
            #alt_texts[any_m].append(re.sub(prefix, '', words))
    #print("\n\n\n{}".format(fname))
    #for k,v in alt_texts.items():
        #for s in v:
            #print("{} \t {} \t {}".format(k,len(v), s))
    
    
