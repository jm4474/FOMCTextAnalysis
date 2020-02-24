import os
import tika
from tika import parser


def extract_and_store(ftype):
    if not os.path.exists("../data/{}_raw_text".format(ftype)):
        os.mkdir("../data/{}_raw_text".format(ftype))
    tika.initVM()
    for fidx, file in enumerate(os.listdir("../data/{}_pdfs".format(ftype))):
        print("{} -- {}".format(fidx, file))
        raw_text = extract_raw_text(ftype, file).encode('utf8')
        raw_text_path = "../data/{}_raw_text/{}".format(ftype, file.replace(".pdf",".txt"))
        with open(raw_text_path, "wb") as f:
            f.write(raw_text)


def extract_raw_text(ftype, file):
    pdf_path = "../data/{}_pdfs/{}".format(ftype, file)
    parsed = parser.from_file(pdf_path)
    raw_text = parsed['content']
    return raw_text

if __name__ == "__main__":
    extract_and_store("minutes")
