%% Meetings in which there is only one mentions of Alternative A

forxls_ALT_A=[Tsummary(numberofsentences_altA==1,1),...
            table(alternativeA(numberofsentences_altA==1))];
        
writetable(forxls_ALT_A,'../Output/Bluebook/CSV/OneMentionA.csv');  

%% Meetings in which there is only one mentions of Alternative B

forxls_ALT_B=[Tsummary(numberofsentences_altB==1,1),...
            table(alternativeB(numberofsentences_altB==1))];
        
writetable(forxls_ALT_B,'../Output/Bluebook/CSV/OneMentionB.csv');

%% Meetings in which there is only one mentions of Alternative C

forxls_ALT_C=[Tsummary(numberofsentences_altC==1,1),...
            table(alternativeC(numberofsentences_altC==1))];
        
writetable(forxls_ALT_C,'../Output/Bluebook/CSV/OneMentionC.csv');

%% Meetings in which there is only one mentions of Alternative C

forxls_ALT_D=[Tsummary(numberofsentences_altD==1,1),...
            table(alternativeD(numberofsentences_altD==1))];
        
writetable(forxls_ALT_D,'../Output/Bluebook/CSV/OneMentionD.csv');