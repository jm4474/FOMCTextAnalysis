%% Analyze statements (INCOMPLETE)

T = readtable('../../Output/Statements/Statements_text.csv');

%% Text of Statements

text ...
  = T.statements;

aux_size ...
  = size(text,1);

FOMC_sentence_dummy ...
  = size(aux_size,1);

FOMC_sentences ...
  = strings(aux_size,1);  

for t_text = 1:aux_size
    
    aux_split ...
        = splitSentences(text(t_text));
    
    aux = (contains(aux_split,'Committee') & contains(aux_split,'decided') & contains(aux_split,'federal funds rate') )...
          | (contains(aux_split,'Committee') & contains(aux_split,'voted') & contains(aux_split,'federal funds rate')) ...
          | (contains(aux_split,'Committee') & contains(aux_split,'target') & contains(aux_split,'federal funds rate')) ...
          | (contains(aux_split,'federal funds rate'));
    
    FOMC_sentence_dummy(t_text,1) ...
        = sum(aux); 
    
    if FOMC_sentence_dummy(t_text,1) == 0 
        
        FOMC_sentences(t_text,1) = 'No sentence containing the search terms';
        
    else
        
        aux_multiple             = aux_split(aux);
        
        FOMC_sentences(t_text,1) = string(aux_multiple(1));
        
    end
        
end
