%% Script to summarize analysis of sentences per meeting

TableAlternatives = readtable(...
 '../../Output/Bluebook/CSV/TableBluebook_matlab_sentencecount.csv');

%% Tabulate the information concerning alternative A
%  .41 seconds

alternatives = ['A','B','C','D','E'];

tic

for i_index  = 1: size(alternatives,2)

tableaux     = tabulate(table2array(TableAlternatives(:,2*(i_index+1))));
      
Number_of_meetings ...
             = tableaux(:,2);
      
Table        = table(tableaux(:,1), Number_of_meetings);

aux1         = strcat('Sentences_mentioning_Alternative',alternatives(1,i_index));

Table.Properties.VariableNames{1}...
             = aux1;
         
aux2         = strcat('Summary_sentences_',alternatives(1,i_index));         

writetable(Table,strcat('../../Output/Bluebook/CSV/',aux2,'.csv'));        
        
clear tableaux Number_of_meetings Table aux1 aux2     

end

toc