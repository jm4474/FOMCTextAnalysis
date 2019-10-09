#!/bin/bash
echo Deleting All Files in Output
rm -rf ../output/*
echo Obtaining Bluebook Alternatives
python obtain_bluebook_alternatives.py
echo Applying Keyword Classifier
python apply_keyword_classifier.py
echo Generating Manual Treatment Validation File
python generate_manual_classifier_treatment_validation_file.py
echo Generating Online Bluebook File
python generate_bluebook_manual_input_online.py
echo Obtaining Statement Outcomes
python obtain_statement_outcomes.py
