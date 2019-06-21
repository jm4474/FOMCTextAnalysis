#!/bin/bash
echo Getting Raw Document Metadata
python download_raw_doc_metadata.py
echo Getting Derived Data
python extract_derived_data.py
echo Downloading Bluebooks
python download_bluebook.py
echo Downloading Statements
python download_statement.py
echo Extracting Raw Text from Statements
python extract_statement_raw_text.py
echo Extracting Raw Text from Bluebooks
python extract_bluebook_raw_text.py
echo Extracting Greenbook Data
python extract_greenbook_data.py
echo Extracting Romer Appendix Data
python extract_romer_appendix.py
echo Finished Execution. Files Viewable in ../output
