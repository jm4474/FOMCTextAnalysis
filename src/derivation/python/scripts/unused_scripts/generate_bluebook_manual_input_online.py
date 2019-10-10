import pandas as pd
'''
@author Anand Chitale
Reads in the mannualy validated treatment file authored by Anand Chitale,
Receives Alternative Data for Alternative D and E(not categorized, also contain
DFEDTR and DFF Info), and merges together to produce an excel file for 
online manual validation by all members

Upon completion, this file contains all treatment and treatment sizes
for every meeting in bluebook sentence period
'''
def main():
    classifier_validate_df = pd.read_excel("../data/manually_validated_treatments.xlsx")
    alternative_d = pd.read_csv("../../Matlab/Output/Bluebook/CSV/SentencesD.csv",encoding="ISO-8859-1")
    alternative_e = pd.read_csv("../../Matlab/Output/Bluebook/CSV/SentencesE.csv",encoding="ISO-8859-1")
    merge_result = merge_alternative_sentences(classifier_validate_df,alternative_d,alternative_e)
    final = transform_merged(merge_result)
    final.to_csv("../output/bluebook_data_for_online.csv")

def merge_alternative_sentences(classifier_validate_df,alternative_d,alternative_e):
    sentence_d_columns = []
    for sentence_num in range(1,9):
        old_sent_name = 'Sentence_'+str(sentence_num)
        new_sent_name = 'Sentence_'+str(sentence_num)+"_alt_d"
        alternative_d[new_sent_name] = alternative_d[old_sent_name]
        sentence_d_columns.append(new_sent_name)
    alternative_d['start_date'] = pd.to_datetime(alternative_d['start_date'])
    alternative_d['C_TREATMENT_alt_d'] = ""
    alt_d_cols = ['start_date','end_date','DFF_Before_meeting','DFEDTR_before',
                                          'DFEDTR_end',"C_TREATMENT_alt_d"]

    for sentence_name in sentence_d_columns:
        alt_d_cols.append(sentence_name)
    alternative_d_subset = alternative_d[alt_d_cols]



    classifier_validate_df['start_date'] = pd.to_datetime(classifier_validate_df['date'])

    merge_classifier_validate_alt_d = classifier_validate_df.merge(alternative_d_subset,on="start_date")

    alternative_e['C_TREATMENT_alt_e'] = ""
    alternative_e['Sentence_1_alt_e'] = alternative_e['Sentence_1']
    alternative_e['start_date'] = pd.to_datetime(classifier_validate_df['start_date'])
    alternative_e_subset = alternative_e[['start_date','C_TREATMENT_alt_e','Sentence_1_alt_e']]

    merge_class_d_e = merge_classifier_validate_alt_d.merge(alternative_e_subset,on="start_date")
    return merge_class_d_e

def transform_merged(merge_class_d_e):
    for alt in ['a','b','c','d','e']:
        merge_class_d_e['C_TREATMENT_SIZE_alt_'+ alt] = ""
        merge_class_d_e['justify_alt_'+alt] = ""
        merge_class_d_e['Sentences_alt_'+alt] = ""
        sentence_columns = []
        for sentence_num in range(1, 12):
            col_name = 'Sentence_' + str(sentence_num) + "_alt_" + alt
            if col_name in merge_class_d_e and type(merge_class_d_e[col_name]=="str"):
                sentence_columns.append(col_name)
        #merge_class_d_e['Sentences_alt_'+alt] = merge_class_d_e[sentence_columns].apply(lambda row: ' '.join(row.values.astype(str)), axis=1)
        for index,row in merge_class_d_e.iterrows():
            sentence_content = []
            for sentence_col in sentence_columns:
                sentence = row[sentence_col]
                if type(sentence)==str:
                    sentence_content.append(sentence)
            merge_class_d_e.at[index,'Sentences_alt_'+alt] = ' '.join(sentence_content)

    merge_class_d_e['comments'] = ""
    merge_sub = merge_class_d_e[[
        'start_date', 'end_date', 'DFF_Before_meeting',
        'DFEDTR_before', 'DFEDTR_end',
        'C_TREATMENT_alt_a', 'C_TREATMENT_SIZE_alt_a', 'justify_alt_a', 'Sentences_alt_a',
        'C_TREATMENT_alt_b', 'C_TREATMENT_SIZE_alt_b', 'justify_alt_b', 'Sentences_alt_b',
        'C_TREATMENT_alt_c', 'C_TREATMENT_SIZE_alt_c', 'justify_alt_c', 'Sentences_alt_c',
        'C_TREATMENT_alt_d', 'C_TREATMENT_SIZE_alt_d', 'justify_alt_d', 'Sentences_alt_d',
        'C_TREATMENT_alt_e', 'C_TREATMENT_SIZE_alt_e', 'justify_alt_e', 'Sentences_alt_e',
        'comments'
    ]]
    return merge_sub

main()