%% Script to add clean text
%PRELIMINARY

Tbluebook   = readtable('../Output/Bluebook/CSV/Bluebook_anand.csv');


%% Extract the clean text
tic

data = cell(size(Tbluebook,1),1);              %Initialize file to save text. 

for t_bbook = 1:size(Tbluebook,1)

data{t_bbook,1} ...
           = extractFileText(strcat('../Output/Bluebook/TXT/',string(Tbluebook.start_date(t_bbook))));
                           
end  

toc

%% Store Text from Bluebooks in a table

Tdata    = table(data); 

Tdata.Properties.VariableNames ...
         = {'clean_file_text'};
     
Tbluebook ...
         = [Tbluebook,Tdata];
     
writetable(Tbluebook,'../Output/Bluebook/CSV/Bluebook_anand_clean.csv');

clearvars -except T_bluebook   