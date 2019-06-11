%% Script to analyze bluebooks
%PRELIMINARY

Tbluebook   = readtable('../Output/Bluebook/CSV/Bluebook_anand.csv');

%% Start date

ind_start   = find(strcmp(Tbluebook.start_date(:,1),'1971-01-12'));

%% Get the text from the file

data        = string(Tbluebook.file_text(ind_start:end));

dates       = Tbluebook.start_date(ind_start:end);

header_aux  = strings(size(data,1),1); 

header      = strings(size(data,1),1);  

header_indicator    ...
            = strings(size(data,1),1);  
 
paragraphs  = strings(size(data,1),1);

%% Separate the files into blocks, according to the bluebook structure

expression  = '(\d{1,2}\)';               %Regular expresssion that looks for (#)

for i_data      = [1:137,139:341]

AUX         = regexp(data(i_data,:),expression,'match'); 
                                           %Extracts all the "(#)" that
                                           %appear at the beginning of the
                                           %paragraph
    
[~,aux,~] = ...
             unique(AUX,'stable');         %Unique occurrences of "(#)"

%% Select the unique numbers 

AUX         = AUX(aux);                    %Unique "(#)"

clear aux

%% Paragraphs 
%  Uses the matlab functions extractBetween and extractAfter to get the
%  paragraphs between the "(n)" and "(n+1)"

for i_para  = 1:size(AUX,2)
    
    if i_para < size(AUX,2)
    
    aux_para = extractBetween(data(i_data,:),AUX(1,i_para),AUX(1,i_para+1),'Boundaries','Inclusive');    
        
    aux_para = extractBefore(aux_para,AUX(1,i_para+1));
    
    paragraphs(i_data,i_para) ...
            = aux_para(1,:);
        
    clear aux_para    
        
    else
        
    aux_para = extractAfter(data(i_data,:),AUX(1,i_para));    
        
    paragraphs(i_data,i_para) ...
            = strcat(AUX(1,i_para),aux_para(1,:));
        
    clear aux_para    
        
    end
    
end

%% Extract the last sentence of each numbered block

header0     = extractBefore(data(i_data,1),'(1)');  

header0     = header0(1,:);

header0_aux = splitSentences(header0);

header0     = header0_aux(end,1);

header_aux(i_data,1) ...
            = header0;

for i_para  = 1:size(AUX,2)-1
   
    aux_para ...
            = splitSentences(paragraphs(i_data,i_para));
        
    header_aux(i_data,i_para+1) ...
            = aux_para(end,1);
        
    clear aux_para    
  
end

clear header0 header0_aux

%% Create a Dummy for each of the elements of header aux that does not end in a period

headers_dummy ...
            = ~ismissing(regexp(header_aux(i_data,:),'\w{1}$','match','once'));

aux_titles  = header_aux(i_data,headers_dummy);

aux_numbers = AUX(1,headers_dummy);

% Eliminate headers if they contain numbers or do not start with caps

dummy_title = ismissing(regexp(aux_titles,'[0-9]','match','once')) & ...
              ~ismissing(regexp(aux_titles,'^[A-Z]','match','once'));
              

aux_titles  = aux_titles(dummy_title);

aux_numbers = aux_numbers(dummy_title);

clear dummy_title
  
for i_title = 1:size(aux_titles,2)

header(i_data,i_title) ...
            = aux_titles(1,i_title);
        
header_indicator(i_data,i_title) ...
            = aux_numbers(1,i_title);
        
end
       
clear aux AUX aux_numbers aux_titles 
  
end