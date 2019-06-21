import pandas as pd
def main():
    df = pd.read_excel("../output/validate_classifier_bluebook_FINAL.xlsx")

    df['date'] = pd.to_datetime(df['date'])

    df_rel_date = df[df['date'].dt.year>=1988]

    alt_a = df_rel_date[['date','alt_a_class','false_a','C_TREATMENT_alt_a']]
    alt_b = df_rel_date[['date', 'alt_b_class', 'false_b', 'C_TREATMENT_alt_b']]
    alt_c = df_rel_date[['date', 'alt_c_class', 'false_c', 'C_TREATMENT_alt_c']]

    alt_a_sent = alt_a[~alt_a['C_TREATMENT_alt_a'].isin(["N","?"])]
    alt_b_sent = alt_b[~alt_b['C_TREATMENT_alt_b'].isin(["N","?"])]
    alt_c_sent = alt_c[~alt_c['C_TREATMENT_alt_c'].isin(["N","?"])]

    alt_with_sent = len(alt_a_sent) + len(alt_b_sent) + len(alt_c_sent)
    print("Total number of alternatives with sentences avilable:{}".format(alt_with_sent))

    correct_a = alt_a_sent[alt_a_sent.false_a == 0]
    correct_b = alt_b_sent[alt_b_sent.false_b == 0]
    correct_c = alt_c_sent[alt_c_sent.false_c == 0]
    print("Total number of correctly predicted sentences:{}"\
          .format(len(correct_a)+len(correct_b)+len(correct_c)))
    print("total number of sentences in alt_a:{}".format(len(alt_a_sent)))
    print("total number of sentences in alt_b:{}".format(len(alt_b_sent)))
    print("total number of sentences in alt_c:{}".format(len(alt_c_sent)))


    print("Number of correctly predicted in alt_a:{}".format(len(correct_a)))
    print("Number of correctly predicted in alt_b:{}".format(len(correct_b)))
    print("Number of correctly predicted in alt_c:{}".format(len(correct_c)))


    succ_a = len(correct_a)/len(alt_a_sent)
    succ_b = len(correct_b)/len(alt_b_sent)
    succ_c = len(correct_c)/len(alt_c_sent)

    print("success rate of {} is {}".format('a',succ_a))
    print("success rate of {} is {}".format('b',succ_b))
    print("success rate of {} is {}".format('c',succ_c))

    overall_success_rate = (len(correct_a)+len(correct_b)+len(correct_c))/(alt_with_sent)
    print("overall success rate: {}".format(overall_success_rate))

    alt_a_treatments = {

    }
    alt_b_treatments = {

    }
    alt_c_treatments = {

    }
    for treatment in ["E","T","U"]:
        alt_a_treatments[treatment] = alt_a_sent[alt_a_sent.C_TREATMENT_alt_a == treatment]
        alt_b_treatments[treatment] = alt_b_sent[alt_b_sent.C_TREATMENT_alt_b == treatment]
        alt_c_treatments[treatment] = alt_c_sent[alt_c_sent.C_TREATMENT_alt_c == treatment]

        print("number of treatment {} in alt a:{}"\
              .format(treatment, len(alt_a_treatments[treatment])))
        print("number of treatment {} in alt b:{}"\
              .format(treatment, len(alt_b_treatments[treatment])))
        print("number of treatment {} in alt c:{}"\
              .format(treatment, len(alt_c_treatments[treatment])))

    for treatment in ["E","T","U"]:
        correct_alt_a_treatment = alt_a_treatments[treatment]\
            [alt_a_treatments[treatment].false_a==0]
        correct_alt_b_treatment = alt_b_treatments[treatment] \
            [alt_b_treatments[treatment].false_b ==0]
        correct_alt_c_treatment = alt_c_treatments[treatment] \
            [alt_c_treatments[treatment].false_c ==0]
        print("number of correct predictions for alt a with treatment {}:{}"
              .format(treatment,len(correct_alt_a_treatment)))
        print("number of correct predictions for alt b with treatment {}:{}"
              .format(treatment,len(correct_alt_b_treatment)))
        print("number of correct predictions for alt c with treatment {}:{}"
              .format(treatment,len(correct_alt_c_treatment)))

        sucess_rate_alt_a_treatment = len(correct_alt_a_treatment)/len(alt_a_treatments[treatment])
        sucess_rate_alt_b_treatment = len(correct_alt_b_treatment)/len(alt_b_treatments[treatment])
        sucess_rate_alt_c_treatment = len(correct_alt_c_treatment)/len(alt_c_treatments[treatment])

        print("Sucess Rate for alt a with treatment {}:{}".format(treatment,sucess_rate_alt_a_treatment))
        print("Sucess Rate for alt b with treatment {}:{}".format(treatment,sucess_rate_alt_b_treatment))
        print("Sucess Rate for alt c with treatment {}:{}".format(treatment,sucess_rate_alt_c_treatment))
        alt_a_treatments["correct_"+treatment] =correct_alt_a_treatment
        alt_b_treatments["correct_"+treatment] =correct_alt_b_treatment
        alt_c_treatments["correct_"+treatment] =correct_alt_c_treatment

    total_e = len(alt_a_treatments["E"]) +len(alt_b_treatments["E"]) + len(alt_c_treatments['E'])
    total_t = len(alt_a_treatments["T"]) +len(alt_b_treatments["T"]) + len(alt_c_treatments['T'])
    total_u = len(alt_a_treatments["U"]) +len(alt_b_treatments["U"]) + len(alt_c_treatments['U'])

    total_correct_e = len(alt_a_treatments["correct_E"]) + \
                      len(alt_b_treatments["correct_E"]) + len(alt_c_treatments['correct_E'])
    total_correct_t = len(alt_a_treatments["correct_T"]) + \
                      len(alt_b_treatments["correct_T"]) + len(alt_c_treatments['correct_T'])
    total_correct_u = len(alt_a_treatments["correct_U"]) + \
                      len(alt_b_treatments["correct_U"]) + len(alt_c_treatments['correct_U'])

    print("Sucess rate Treatment E:{}".format(total_correct_e/total_e))
    print("Sucess rate Treatment T:{}".format(total_correct_t/total_t))
    print("Sucess rate Treatment U:{}".format(total_correct_u/total_u))


main()