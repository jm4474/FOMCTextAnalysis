import os
import re 

alternatives = re.compile(r'alternative ([abc]) ')
prefix = re.compile(r'^ ?\( ?\d{1,2} ?\)')

SENT_BOUND="$$$___$$$"

def split_bluebook(fname, outdir=""):
    print("\n", fname)
    content = open(fname).read()
    paragraphs = {}
    this_key=0
    for sentence in content.split("\n\n"):
        words = " ".join([w.split("\t")[0] for w in sentence.split("\n")])
        # some cleanup
        words = words.replace('alterna- tive', 'alternative').replace('alter- native', 'alternative').replace('alterna- tives', 'alternatives')
        for alt in ['a', 'b', 'c', 'd']:
            words = re.sub(r'alternative {}([.,;?!:()])'.format(alt), r'alternative {} \1'.format(alt), words)
        if prefix.findall(words):
            this_key = int(prefix.findall(words)[0].strip("() "))
        if this_key not in paragraphs:
            paragraphs[this_key]=[]
        if not "table 1 : " in words:
            paragraphs[this_key].append(words)
    
    paragraphs = fix_paragraphs(paragraphs)
    paragraph_alts = get_paragraph_alternatives(paragraphs, "dist")
    
    #for k in sorted(list(paragraphs.keys())):
        #print(k, paragraph_alts[k], sum([paragraphs[k] for paragraphs[k] in paragraph_alts[k].values()]))
    
    if outdir!="":
        print(len(paragraphs.keys()))
        #print(paragraphs)
        with open(os.path.join(outdir, fname.split('/')[-1]), 'w+') as of:
            for k in sorted(list(paragraphs.keys())):
                of.write("{}\n".format(paragraph_alts[k]))
                for s in paragraphs[k].split(SENT_BOUND):
                    of.write("{}\n".format(s))
                of.write("\n")
        
        #for s in v:
            #print("{} \t {} \t {}".format(k,len(v), s))
    
    
    
def replace_nums_to_letters(ps):
    for k in ps.keys():
        ps[k] = re.sub(r'alternative i([ ,.?!])', r'alternative a\g<1>', ps[k])
        ps[k] = re.sub(r'alternative ii([ ,.?!])', r'alternative b\g<1>', ps[k])
        ps[k] = re.sub(r'alternative iii([ ,.?!])', r'alternative c\g<1>', ps[k])
        ps[k] = re.sub(r'alternative iv([ ,.?!])', r'alternative d\g<1>', ps[k])
    return ps
    
def fix_paragraphs(ps):
    ps = {k:SENT_BOUND.join(v) for k,v in ps.items()}
    ps = replace_nums_to_letters(ps)
    changed=True
    while changed:
        changed=False
        pkeys = sorted(list(ps.keys()))
        #print(pkeys)
        for idx in range(1, len(pkeys)+1):
            if idx==len(pkeys) or pkeys[idx] != pkeys[idx-1]+1:
                tmp = re.split(r'\( ?{} ?\)'.format(pkeys[idx-1]+1), ps[pkeys[idx-1]])
                if len(tmp)==2:
                    ps[pkeys[idx-1]+1] = '( {} ) '.format(pkeys[idx-1]+1)+tmp[1]
                    ps[pkeys[idx-1]] = tmp[0]
                    changed=True                   
    return ps



def get_paragraph_alternatives(paragraphs, typ="dist"):
    if typ=="dist": # compute distribution over mentions
        paragraph_alternatives = {key:{'a':0, 'b':0, 'c':0, 'd':0, 'two':0} for key in paragraphs.keys()}
        for par, sents in paragraphs.items():
            paragraph_alternatives[par]['a'] = sents.count('alternative a ')
            paragraph_alternatives[par]['b'] = sents.count('alternative b ')
            paragraph_alternatives[par]['c'] = sents.count('alternative c ')
            paragraph_alternatives[par]['d'] = sents.count('alternative d ')
            paragraph_alternatives[par]['two'] = re.findall('alternatives [abc] (?:and|or) [abc] ', sents)
    elif typ=="first": # return first mention of alternative
        paragraph_alternatives = {key:{} for key in paragraphs.keys()}
        for par, sents in paragraphs.items():
            matches = re.findall('alternative ([abcd])', sents)
            if matches:
                paragraph_alternatives[par] = {matches[0]:matches.count(matches[0])}
            else:
                paragraph_alternatives[par]  = {-1:-1}
    return paragraph_alternatives



    
def main():
    indir = "/home/lea/academic/melbourne/research/fed_causal/data/bluebook_raw_text/preprocessed"
    outdir = "/home/lea/academic/melbourne/research/fed_causal/data/bluebook_raw_text/paragraphs_dist2"
    infiles = os.listdir(indir)
    for f in infiles:
        if f.endswith(".txt"):# and 1987<=int(f.split('-')[0])<=2009:
            split_bluebook(os.path.join(indir, f), outdir)
    
    
    
    

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
    
    
