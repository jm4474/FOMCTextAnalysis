%% Script to Download Statements

T = readtable('../../../derived_data.csv');

%% Eliminate extra spaces

T.file_name = strtrim(T.file_name);        %Remove extra spaces in the file_name

T.grouping = strtrim(T.grouping);          %Remove extra spaces in the file_type

%% Filter Statements

 Tstatements ...
           = T(string(T.grouping) == 'Statement',:);
       
%% Store in a string array

aux_size   = size(Tstatements,1);

statements = strings(aux_size,1);

options    = weboptions;

options.Timeout ...
           = 15;

tic;

for t_statement = 1:aux_size

   if strcmp(string(Tstatements.file_type(t_statement)),'HTML') 
    
   statements(t_statement,1) ...
           = extractHTMLText(webread(string(Tstatements.link(t_statement)),options));
       
   else 
    
   statements(t_statement,1) ...
           = 'CHECK';
       
   end       

end

toc;

%% Save csv file with the text of the statements 

T_text ...
     = [Tstatements, table(statements) ];

writetable(T_text,'../../Output/Statements/Statements_text.csv');

clearvars -except T_text