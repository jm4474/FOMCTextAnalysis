import pandas as pd

def main():
    alternative_a = pd.read_excel("../../Matlab/Output/Bluebook/CSV/CommentedFiles/SentencesA_commented.xlsx")
    alternative_b = pd.read_excel("../../Matlab/Output/Bluebook/CSV/CommentedFiles/SentencesB_commented.xlsx")
    alternative_c = pd.read_excel("../../Matlab/Output/Bluebook/CSV/CommentedFiles/SentencesC_commented.xlsx")
    classified_data = pd.read_csv("../output/bluebook_alt_and_class_output.csv")
    classified_data['date'] = pd.to_datetime(classified_data['meeting_date'])
    alternative_a['date'] = pd.to_datetime(alternative_a['start_date'])
    alternative_b['date'] = pd.to_datetime(alternative_b['start_date'])
    alternative_c['date'] = pd.to_datetime(alternative_c['start_date'])
    treatment_csv(alternative_a, alternative_b, alternative_c, classified_data)


def treatment_csv(alternative_a, alternative_b, alternative_c, classified_data):
    alt_columns = ['date','C_TREATMENT','KEYWORDS_TREATMENT','']
    for sent_num in range(1,13):
        alt_columns.append("Sentence_"+str(sent_num))
    to_merge_a = alternative_a.filter(alt_columns)
    to_merge_b = alternative_b.filter(alt_columns)
    to_merge_c = alternative_c.filter(alt_columns)
    to_merge_a.columns = to_merge_a.columns.map(lambda x: x + '_alt_a' if x != 'date' else x)

    merged_b_c = to_merge_b.merge(to_merge_c,suffixes=("_alt_b","_alt_c"),
                                     on="date")

    merged_a_b_c = merged_b_c.merge(to_merge_a,on="date")

    to_merge_classified = classified_data.filter(['date','alt_a_class','alt_b_class','alt_c_class'])

    merged_a_b_c_classifier = to_merge_classified.merge(merged_a_b_c,on="date")


    merged_a_b_c_classifier = merged_a_b_c_classifier[[
        'date','alt_a_class','C_TREATMENT_alt_a', 'KEYWORDS_TREATMENT_alt_a',
        'Sentence_1_alt_a', 'Sentence_2_alt_a', 'Sentence_3_alt_a',
        'Sentence_4_alt_a', 'Sentence_5_alt_a', 'Sentence_6_alt_a',
        'Sentence_7_alt_a', 'Sentence_8_alt_a', 'Sentence_9_alt_a',
        'Sentence_10_alt_a',
        'alt_b_class',
        'C_TREATMENT_alt_b', 'KEYWORDS_TREATMENT_alt_b', 'Sentence_1_alt_b',
        'Sentence_2_alt_b', 'Sentence_3_alt_b', 'Sentence_4_alt_b',
        'Sentence_5_alt_b', 'Sentence_6_alt_b', 'Sentence_7_alt_b',
        'Sentence_8_alt_b', 'Sentence_9_alt_b', 'Sentence_10_alt_b',
        'Sentence_11_alt_b', 'Sentence_12_alt_b',
        'alt_c_class',
        'C_TREATMENT_alt_c','KEYWORDS_TREATMENT_alt_c', 'Sentence_1_alt_c',
        'Sentence_2_alt_c', 'Sentence_3_alt_c', 'Sentence_4_alt_c', 'Sentence_5_alt_c',
        'Sentence_6_alt_c', 'Sentence_7_alt_c', 'Sentence_8_alt_c',
        'Sentence_9_alt_c', 'Sentence_10_alt_c', 'Sentence_11_alt_c',
        'Sentence_12_alt_c']]
    merged_a_b_c_classifier.to_csv("../output/validate_classifier_bluebook.csv")

main()