%% Script to split the text of the bluebooks sentence by sentence

Tbluebook = readtable('../../Output/Bluebook/CSV/TableBluebook_matlab_extraction.csv');

%% Start date and End date

ind_start   = find(strcmp(string(Tbluebook.start_date(:,1)),'1968-08-13'));

ind_end     = find(strcmp(string(Tbluebook.start_date(:,1)),'2009-03-17'));

%Comment: we focus on this period because the bluebooks over
%this sample have numbered block of paragraphs. 

data        = string(Tbluebook.TextBluebook(ind_start:ind_end));

dates       = Tbluebook.start_date(ind_start:ind_end);

%% Define regular Expression and look for alternatives

expression = '([Aa]lternative\s+[AaBbCcDdEe][^a-z])';

aux        = regexp(data,expression,'match'); 
                                            %Cell Indicating the number of
                                            %paragraphs that contain the
                                            %regular expression


%% Look for alternative A B C D E: initialize variables

alternativeA = strings(size(data,1),1);

numberofsentences_altA ...
             = zeros(size(data,1),1);
         
alternativeB = strings(size(data,1),1);

numberofsentences_altB ...
             = zeros(size(data,1),1);         

alternativeC = strings(size(data,1),1);

numberofsentences_altC ...
             = zeros(size(data,1),1);  
         
alternativeD = strings(size(data,1),1);

numberofsentences_altD ...
             = zeros(size(data,1),1);  
         
alternativeE = strings(size(data,1),1);

numberofsentences_altE ...
             = zeros(size(data,1),1);           

%% Look for alternative A B C D E: loop       
         
tic         
         
for i_data = 1:size(data,1)

if cellfun(@isempty,aux(i_data))

alternativeA(i_data,:) = 'No Sentences Alternative A';    
    
alternativeB(i_data,:) = 'No Sentences Alternative B';   

alternativeC(i_data,:) = 'No Sentences Alternative C'; 

alternativeD(i_data,:) = 'No Sentences Alternative D'; 

alternativeE(i_data,:) = 'No Sentences Alternative E'; 

else    
    
aux_sentences ...
     = splitSentences(data(i_data,1));

expressionA ...
     = '[Aa]lternative\s+[Aa][^a-z]';
 
expressionB ...
     = '[Aa]lternative\s+[Bb][^a-z]'; 
 
expressionC ...
     = '[Aa]lternative\s+[Cc][^a-z]'; 
 
expressionD ...
     = '[Aa]lternative\s+[Dd][^a-z]'; 
 
expressionE ...
     = '[Aa]lternative\s+[Ee][^a-z]'; 
 
sentencesA ...
     = aux_sentences(~ismissing(regexp(aux_sentences,expressionA,'match','once')));  

if isempty(sentencesA)
   
numberofsentences_altA(i_data,1) ...
      = 0;
  
alternativeA(i_data,:) ...
     = 'No Sentences Alternative A';  
    
else 
 
numberofsentences_altA(i_data,1) ...
     = size(sentencesA,1);
 
alternativeA(i_data,:) ...
     = join(sentencesA);
 
end
 
sentencesB ...
     = aux_sentences(~ismissing(regexp(aux_sentences,expressionB,'match','once')));  

if isempty(sentencesB)
   
numberofsentences_altB(i_data,1) ...
      = 0;
  
alternativeB(i_data,:) ...
     = 'No Sentences Alternative B';  
    
else  
 
numberofsentences_altB(i_data,1) ...
     = size(sentencesB,1);
 
alternativeB(i_data,:) ...
     = join(sentencesB); 
 
end 
 
sentencesC ...
     = aux_sentences(~ismissing(regexp(aux_sentences,expressionC,'match','once')));  
 
if isempty(sentencesC)
   
numberofsentences_altC(i_data,1) ...
      = 0;
  
alternativeC(i_data,:) ...
     = 'No Sentences Alternative C';  
    
else  
 
numberofsentences_altC(i_data,1) ...
     = size(sentencesC,1);
 
alternativeC(i_data,:) ...
     = join(sentencesC); 
 
end

sentencesD ...
     = aux_sentences(~ismissing(regexp(aux_sentences,expressionD,'match','once')));  
 
if isempty(sentencesD)
   
numberofsentences_altD(i_data,1) ...
      = 0;
  
alternativeD(i_data,:) ...
     = 'No Sentences Alternative D';  
    
else  
 
numberofsentences_altD(i_data,1) ...
     = size(sentencesD,1);
 
alternativeD(i_data,:) ...
     = join(sentencesD); 
 
end

sentencesE ...
     = aux_sentences(~ismissing(regexp(aux_sentences,expressionE,'match','once')));  
 
if isempty(sentencesE)
   
numberofsentences_altE(i_data,1) ...
      = 0;
  
alternativeE(i_data,:) ...
     = 'No Sentences Alternative E';  
    
else  
 
numberofsentences_altE(i_data,1) ...
     = size(sentencesE,1);
 
alternativeD(i_data,:) ...
     = join(sentencesE); 
 
end

 
end 

end

toc

clear sentencesA sentencesB sentencesC sentencesD sentences E relavant_paragraphs

%% Create Table

TableAlternatives = [Tbluebook(ind_start:ind_end,1:3), ...
                     table(numberofsentences_altA), table(alternativeA),...
                     table(numberofsentences_altB), table(alternativeB),...
                     table(numberofsentences_altC), table(alternativeC),...
                     table(numberofsentences_altD), table(alternativeD),...
                     table(numberofsentences_altE), table(alternativeE)];                 
%% Store in csv files                
                     
writetable(TableAlternatives,'../../Output/Bluebook/CSV/TableBluebook_matlab_sentencecount.csv');
