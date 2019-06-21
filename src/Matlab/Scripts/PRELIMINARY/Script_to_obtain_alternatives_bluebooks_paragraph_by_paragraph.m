%% Scripts to analyze Bluebooks (paragraph by paragraph)

load('../Output/Bluebook/MAT/Paragraphs.mat');

%% Convert table to string array

Paragraphs = table2array(Tpara(:,3:end));

%% Display:

disp('The total number of available paragraphs from')

disp(Tpara.start_date(1)) 

disp('to')

disp(Tpara.start_date(end)) 

disp('is')

disp(sum(sum(~cellfun(@isempty,Paragraphs))));

%% Search for Alternative A and Funds rate

aux        = regexp(Paragraphs,'([Aa]lternative\s+[AaBbCcDd])','match');

%% Check how many paragraphs contain the expressions above

dummyempty = ~cellfun(@isempty,aux);

disp('There are')

disp(sum(sum(dummyempty)))

disp('that contains the expressions Alternative A, B, C, D.')

%% Create a table that contains how many paragraphs per document mentions alternative

Tnonempty  = table(Tpara.start_date,...
                 Tpara.end_date); 

Tnonempty.Properties.VariableNames ...
         = {'start_date','end_date'};

Tnonempty  = [Tnonempty,table(sum(dummyempty,2))];

Tnonempty.Properties.VariableNames{end} ...
           = 'RelevantParagraphs';

%% Display sentences with a paragraph/date identifier

dates_aux = repmat(Tnonempty.start_date,[1,size(Paragraphs,2)]);

Paragraphs_aux ...
          = repmat(1:size(Paragraphs,2),[size(Paragraphs,1),1]);
      
      
%% 

NonEmptyParagraphs ...
         = [ dates_aux(~cellfun(@isempty,aux)),...
             Paragraphs_aux(~cellfun(@isempty,aux)),...
             Paragraphs(~cellfun(@isempty,aux))];
         
         
         
%% Add a fourt paragraph with the mentions of the alternatives

aux2     = aux(~cellfun(@isempty,aux));



for i_var= 1: size(aux2,1)
   
    NonEmptyParagraphs(i_var,4) ...
         = join(aux2{i_var},', ');
    
end

save('../Output/Bluebook/MAT/Paragraphs_discuss_alternatives.mat','NonEmptyParagraphs'); 
 
%% TO DO: figure out how to properly save the table as a csv

%table_nonempty ...
            %= table(NonEmptyParagraphs(:,1),NonEmptyParagraphs(:,2),NonEmptyParagraphs(:,3),NonEmptyParagraphs(:,4));

%table_nonempty.Properties.VariableNames... 
            %= {'start_date','Paragraph_number','Paragraph','Alternatives'};
        
%writetable(table_nonempty,'../Output/Bluebook/CSV/TableBluebook_Paragraph_Alternatives.csv');        
        
%|[Aa]lternative\s+[Bb]|[Aa]lternative\s+[Cc]

%% aux rate

aux_rate    = regexp(NonEmptyParagraphs(:,3),'federal funds|funds rate|target','match');

for i_var= 1: size(aux_rate,1)
    
    if isempty(aux_rate{i_var})
    
    NonEmptyParagraphs(i_var,5) = 'Not Found';    
        
    else    
        
    NonEmptyParagraphs(i_var,5) ...
         = join(aux_rate{i_var},', ');
     
    end
    
end

%% aux_percent

aux_percent = regexp(NonEmptyParagraphs(:,3),'per cent|percent|\%|unchanged','match');

for i_var= 1: size(aux_percent,1)
    
    if isempty(aux_percent{i_var})
    
    NonEmptyParagraphs(i_var,6) = 'Not Found';    
        
    else    
        
    NonEmptyParagraphs(i_var,6) ...
         = join(aux_percent{i_var},', ');
     
    end
    
end

%% 

aux_alt_rates ...
            = NonEmptyParagraphs(~cellfun(@isempty,aux_percent) & ~cellfun(@isempty,aux_rate),:);

%% 

disp('Out of these meetings we have')

disp(size(aux_alt_rates,1)) 

disp('that contain also the words federal funds and percent')

%% 

sentences     = strings(size(aux_alt_rates,1),1);

for i_data    = 1:size(aux_alt_rates,1)

aux_sentences = splitSentences(aux_alt_rates(i_data,3));

dummy_all_1     = contains(aux_sentences,split(aux_alt_rates(i_data,4),',')); 
  
dummy_all_2     = contains(aux_sentences,split(aux_alt_rates(i_data,5),',')); 
    
dummy_all_3     = contains(aux_sentences,split(aux_alt_rates(i_data,6),','));
                
aux_sentences_dummy_all ...
              = aux_sentences(dummy_all_1& dummy_all_2 & dummy_all_3);

if isempty(aux_sentences_dummy_all)          
 
sentences(i_data,1) ...
              = 'No sentence found containing all of the search terms';
    
else    

for i_sentence = 1:size(aux_sentences_dummy_all,1)    
    
sentences(i_data,i_sentence) ...
              = aux_sentences_dummy_all(i_sentence,1);
          
end
          
end          
%NonEmptyParagraphs(i_data,7) ...
              %= join(aux_sentences_dummy_all,'|||');

end

%%

Final_data = [aux_alt_rates,sentences];

%% 


