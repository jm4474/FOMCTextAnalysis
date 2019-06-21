%% Script to Extract Text from the Bluebook PDF files

T = readtable('../../derived_data.csv');

%% Eliminate extra spaces

T.file_name = strtrim(T.file_name);        %Remove extra spaces in the file_name

T.grouping = strtrim(T.grouping);          %Remove extra spaces in the file_type

%% Filter Bluebooks

Tbluebook ...
           = T(string(T.grouping) == 'Bluebook',:);
       
clear T;       
       
%% Extract Text (Takes around 60 seconds)    

tic

data = strings(size(Tbluebook,1),1);              %Initialize file to save text. 

for t_bbook = 1:size(Tbluebook,1)

datafrompdf ...
           = strtrim(extractFileText(strcat('../Output/Bluebook/PDFs/bluebook',num2str(t_bbook),'.pdf')));
       
data_no_breaks ...
           = regexprep(datafrompdf,'[\n\r]+',' ');     %Replaces line break by space
       
data(t_bbook,1) ...
           = erase(data_no_breaks,strcat('-',{' '}));
       
clear datafrompdf data_no_breaks       
       
end  

toc

%% Store Text from Bluebooks in a table

Tdata    = table(data); 

Tdata.Properties.VariableNames ...
         = {'TextBluebook'};
     
Tbluebook ...
         = [Tbluebook,Tdata];
     
writetable(Tbluebook,'../Output/Bluebook/CSV/TableBluebook.csv');

clearvars -except T_bluebook   
