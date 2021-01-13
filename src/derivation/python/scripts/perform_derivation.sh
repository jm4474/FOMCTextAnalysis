#!/bin/bash
echo Deleting All Files in Output
rm -rf ../output/*
echo Obtaining Bluebook Alternatives
python obtain_bluebook_alternatives.py
echo Produce Bluebook Stats
python produce_bluebook_stats.py
echo Obtaining Statement Outcomes
python obtain_statement_outcomes.py
echo Applying Keyword Classifier
python apply_keyword_classifier.py
echo Produce Federal Funds Future Data
python derive_federalfundsfuture_data.py
echo Produce News Data
python produce_master_news.py
echo Produce Meeting Derived File
python produce_meeting_derived_file.py
echo Produce Daily Policy Data
python produce_daily_policy_data.py
echo Produce Market Expectations
python extract_market_expectations.py
echo Produce Separated Transcripts
python transcript_file.py

