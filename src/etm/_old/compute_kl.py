import numpy as np

for data in ["mindf_10_30_all_2_google_emb",
             "mindf_10_10_google_embed",
             "mindf_10_30_all_google_emb",
             "30_all_google_emb",
            "all_large_embeddings",
             "30_all",
             "bluebooks", 
             "bluebooks_train_embeddings",
             "all",
             "all_train_embeddings",
             "all_subsampled",
             "all_subsampled_train_embeddings"]:
    
    performance = []
    outfile = open("../performance_by_year_{}.tsv".format(data), 'w+')
    with open("../thetas_by_year_{}.tsv".format(data), 'r') as infile:
        meetings = infile.read().split("\n\n")
        for meeting in meetings:
            correct_cnt=0
            total=0
            date = meeting.split("\n")[0]
            speakers = [speaker.split("\t") for speaker in meeting.split("\n")[1:] if len(speaker.split("\t"))==4 and speaker.split("\t")[2].startswith("alt")]
            
            if len(speakers)>0:
            
                alternatives = [speaker.split("\t") for speaker in meeting.split("\n")[1:] if len(speaker.split("\t"))==4 and not speaker.split("\t")[2].startswith("alt")]
                
                speaker_alt_sims = {}
                for speaker in speakers:
                    total+=1
                    lowest = 10000
                    lowestalt = ""
                    speaker_alt_sims[speaker[0]] = {"voted":speaker[2]}
                    theta_s = np.asarray([float(f) for f in speaker[3].strip("[]").split(",")], dtype=np.float)
                    for alt in alternatives:
                        theta_a = np.asarray([float(f) for f in alt[3].strip("[]").split(",")], dtype=np.float)
                        kl = np.sum(np.where(theta_s != 0, theta_s * np.log(theta_s / theta_a), 0))
                        #kl = np.sqrt(1 - np.sum(np.sqrt(np.multiply(theta_s,theta_a))))
                        speaker_alt_sims[speaker[0]][alt[1]]=kl
                        if kl < lowest:
                            lowestalt = alt[1]
                            lowest = kl
                    if lowestalt == speaker_alt_sims[speaker[0]]["voted"]:
                        speaker_alt_sims[speaker[0]]["correct"]=True
                        correct_cnt+=1
                performance.append(correct_cnt / total)
                outfile.write("\n{}\t{}\n".format(date, correct_cnt / total))
                for k,v in speaker_alt_sims.items():
                    correct=''
                    if 'correct' in v:
                        correct='**'
                    outfile.write("{}\t{}\t{}\n".format(correct, k, v))
                outfile.write("\n")
        outfile.write("performance {}".format(np.mean(performance)))
