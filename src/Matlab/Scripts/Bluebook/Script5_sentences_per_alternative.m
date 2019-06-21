%% Script to generate a CSV file with the sentences for each alternative

% Load the sentence count for each alternative

TableAlternatives = readtable(...
 '../../Output/Bluebook/CSV/TableBluebook_matlab_sentencecount.csv');

%% Add value of the federal funds rate the day before the meeting

TFedFunds = readtable('../../Data/DFF_FRED.xlsx');

datesFedFunds ...
          = string(datetime(TFedFunds.observation_date(:,1),'Format','yyyy-MM-dd'));

daybeforemeeting ...
          = TableAlternatives.start_date-1;
      
indices   = sum((string(daybeforemeeting)==datesFedFunds'),1)==1;

TFedFunds = TFedFunds(indices',2);

TFedFunds.Properties.VariableNames{1} ...
          = 'DFF_Before_meeting';

clear indices datesFedFunds 

%% For reference, add the Romer and Romer intended Federal Funds Rate at the end of the meeting 
%  (and the monetary policy decision)

TDFEDTR   = readtable('../../Data/DFEDTAR_FRED.xlsx');

datestarget ...
          = string(datetime(TDFEDTR.observation_date(:,1),'Format','yyyy-MM-dd'));

dayendmeeting ...
          = TableAlternatives.end_date;
            
DFEDTR_end ...
          = strings(size(TFedFunds,1),1);

%Fill the end of the meeting DFEDTR      
for i_date= 1:size(TFedFunds,1)      
    
    aux   = strcmp(string(dayendmeeting(i_date,1)),datestarget);
    
    if sum(aux)==0
        
        DFEDTR_end(i_date,1) = 'No target in FRED';
        
    else
        
        DFEDTR_end(i_date,1) = TDFEDTR.DFEDTAR(aux,1);
       
    end
    
end

clear aux

DFEDTR_before ...
          = strings(size(TFedFunds,1),1);


%Fill the before the meeting DFEDTR
for i_date= 1:size(TFedFunds,1)      
    
    aux   = strcmp(string(daybeforemeeting(i_date,1)),datestarget);
    
    if sum(aux)==0
        
        DFEDTR_before(i_date,1) = 'No target in FRED';
        
    else
        
        DFEDTR_before(i_date,1) = TDFEDTR.DFEDTAR(aux,1);
       
    end
    
end



clear TDFEDTR 

TDFEDTR  = table(DFEDTR_before,DFEDTR_end);

clear indices dayendmeeting datestarget DFEDTR daybeforemeeting

%% Generate csv files with the sentences for each alternative
%  Takes 11 seconds

alternatives = ['A','B','C','D','E'];

tic

for i_index  = 1: size(alternatives,2)

max_sentences ...
             = max(table2array(TableAlternatives(:,2*(i_index+1))));

sentences    = strings(size(TableAlternatives,1),max_sentences);


for i_data = 1:size(TableAlternatives,1)
    
if table2array(TableAlternatives(i_data,2*(i_index+1))) == 0 
    
    sentences(i_data,1) ...
           = string(TableAlternatives{i_data,2*(i_index+1)+1});
       
else 
    
    aux    = splitSentences(string(TableAlternatives{i_data,2*(i_index+1)+1}));
    
    sentences(i_data,1:size(aux,1)) ...       
           = string(aux');
       
    clear aux   
    
end
        
end

T         = [TableAlternatives(:,1:3),TableAlternatives(:,2*(i_index+1)),TFedFunds,TDFEDTR, table(sentences(:,1))]; 

T.Properties.VariableNames{end} = 'Sentence_1';

for i_sentences = 1:max_sentences-1
   
    T     = [T,table(sentences(:,i_sentences+1))];
    
    T.Properties.VariableNames{end} = strcat('Sentence_',num2str(i_sentences+1));
    
end

%%

writetable(T,strcat('../../Output/Bluebook/CSV/Sentences',alternatives(1,i_index),'.csv'));

end

toc