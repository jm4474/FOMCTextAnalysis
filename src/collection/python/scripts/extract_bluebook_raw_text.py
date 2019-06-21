import os
import tika
from tika import parser

#This file extracts the raw text of downloaded bluebook pdf documents

def extract_bluebook_raw_text():
    if not os.path.exists("../output/bluebook_raw_text"):
        os.mkdir("../output/bluebook_raw_text")
    tika.initVM()
    for file in os.listdir("../output/bluebook_pdfs"):
        raw_text = extract_raw_text(file)
        raw_text_path = "../output/bluebook_raw_text/{}".format(file.replace(".pdf",".txt"))
        with open(raw_text_path, "w") as f:
            f.write(raw_text)


def extract_raw_text(file):
    pdf_path = "../output/bluebook_pdfs/{}".format(file)
    parsed = parser.from_file(pdf_path)
    raw_text = parsed['content']
    return raw_text

if __name__ == "__main__":
    extract_bluebook_raw_text()