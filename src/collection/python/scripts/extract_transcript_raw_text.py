import os
import tika
from tika import parser

'''
@Author Anand Chitale
This file extracts the raw text of already downloaded transcript pdf documents
using the tika parser and outputs raw text files into the output folder 
transcript_raw_text
'''
def extract_transcript_raw_text():
    if not os.path.exists("../output/transcript_raw_text"):
        os.mkdir("../output/transcript_raw_text")
    tika.initVM()
    for file in os.listdir("../output/transcript_pdfs"):
        raw_text = extract_raw_text(file).encode('utf8')
        raw_text_path = "../output/transcript_raw_text/{}".format(file.replace(".pdf",".txt"))
        with open(raw_text_path, "wb") as f:
            f.write(raw_text)


def extract_raw_text(file):
    pdf_path = "../output/transcript_pdfs/{}".format(file)
    parsed = parser.from_file(pdf_path)
    raw_text = parsed['content']
    return raw_text

if __name__ == "__main__":
    extract_transcript_raw_text()