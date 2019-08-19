rm -r ../../output/overleaf_files
mkdir ../../output/overleaf_files
python analyze_statements.py
python decade_file_counts.py
python generate_rateless_alt_action.py
python obtain_sumstats_bb_options.py
python produce_bb_size_sumstats.py
python produce_federal_funds_graphs.py
python produce_grouped_percent_treatment.py
python produce_news_stats.py
python produce_rate_change_source.py
python produce_sumstats_menu.py
python produce_target_and_alternative_data.py