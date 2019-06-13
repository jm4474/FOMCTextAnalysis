%% Scripts to analyze Bluebooks (paragraph by paragraph)

load('../Output/Bluebook/MAT/Paragraphs.mat');

%% Convert table to string array

Paragraphs = table2array(Tpara(:,3:end));

%% Search for Alternative A and Funds rate

aux        = regexp(Paragraphs,'([Aa]lternative\s+[Aa]|[Aa]lternative\s+[Bb]|[Aa]lternative\s+[Cc])','match');

%% Check how many paragraphs contain the expressions above

dummyempty = ~cellfun(@isempty,aux);

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
       
%% aux rate

aux_rate    = regexp(NonEmptyParagraphs(:,3),'federal funds|funds rate|target','match');

aux_percent = regexp(NonEmptyParagraphs(:,3),'per cent|percent','match');

aux_alt_rates ...
            = NonEmptyParagraphs(~cellfun(@isempty,aux_percent) & ~cellfun(@isempty,aux_rate),:);
