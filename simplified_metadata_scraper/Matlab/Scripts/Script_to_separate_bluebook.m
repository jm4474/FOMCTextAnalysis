%% Script to separate bluebooks paragraph by paragraph
%  This version: June 12th, 2019

Tbluebook   = readtable('../Output/Bluebook/CSV/Bluebook_anand.csv');

%% Extract clean text
tic

Tbluebook.clean_file_text = strings(size(Tbluebook,1),1);              %Initialize file to save text. 

for t_bbook = 1:size(Tbluebook,1)

Tbluebook.clean_file_text(t_bbook,1) ...
           = extractFileText(strcat('../Output/Bluebook/TXT/',string(Tbluebook.start_date(t_bbook))));
                           
end  

toc         %Approximately 15 seconds

%% Start date

ind_start   = find(strcmp(Tbluebook.start_date(:,1),'1968-08-13'));

ind_end     = find(strcmp(Tbluebook.start_date(:,1),'2009-03-17'));

%% Get the text from the file

data        = string(Tbluebook.clean_file_text(ind_start:ind_end));

dates       = Tbluebook.start_date(ind_start:ind_end);

header_aux  = strings(size(data,1),1); 

header      = strings(size(data,1),1);  

header_indicator    ...
            = strings(size(data,1),1);  
 
paragraphs  = strings(size(data,1),1);

%% Separate the files into blocks, according to the bluebook structure

expression  = '\n{1} ?\(\s?\d{1,2}\s?\)\s+(\"|[A-Z]{1})';               %Regular expresssion that looks for (#)

tic

for i_data      = [1:170,172:size(data,1)]

AUX         = regexp(data(i_data,:),expression,'match'); 
                                           %Extracts all the "(#)" that
                                           %appear at the beginning of the
                                           %paragraph
                                           
expressionaux ...
            = '\n{1} ?\(\s?\d{1,2}\s?\)';
        
AUX         = string(regexp(AUX,expressionaux,'match'));        
    
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

header0     = strtrim(header0(1,:));

header0     = replace(header0,char(10),'.');

header0_aux = splitSentences(header0);

header0     = header0_aux(end,1);

header_aux(i_data,1) ...
            = header0;

for i_para  = 1:size(AUX,2)-1
   
    aux_para_1...
            = strtrim(paragraphs(i_data,i_para));
            
    aux_para_2 ...
            = splitSentences(aux_para_1); clear aux_para_1
        
    aux_para_3 ...
            = splitSentences(strtrim(replace(aux_para_2(end,1),char(10),' .'))); clear aux_para_2  %IMPORTANT LINE!
        
    header_aux(i_data,i_para+1) ...
            = aux_para_3(end,1);     
        
    clear aux_para_3    
  
end

clear header0 header0_aux

%% Create a Dummy for each of the elements of header aux that does not end in a period

headers_dummy ...
            = ~ismissing(regexp(header_aux(i_data,:),'\w{1}$','match','once'));

aux_titles  = header_aux(i_data,headers_dummy);

aux_numbers = AUX(1,headers_dummy);

% Eliminate headers if they contain numbers or do not start with caps

dummy_title = ismissing(regexp(aux_titles,'[0-9]','match','once')) & ...       %No Numbers
              ismissing(regexp(aux_titles,'\n+','match','once'))&...           %No line breaks
              ~ismissing(regexp(aux_titles,'^[A-Z]','match','once'))&...       %First Cap
              ~ismissing(regexp(aux_titles,'\w{2}','match','once'))&...        %At least two consecutive words
              ~ismissing(regexp(aux_titles,'^\w{2}','match','once'))&...       %At least two consecutive words at the beginning
              ismissing(regexp(aux_titles,',','match','once'))&...             %No commas
              ismissing(regexp(aux_titles,'(\w+\s\w+){7}','match','once'))&... %No titles with 8 words or more
              ismissing(regexp(aux_titles,'(Paths? Actual)','match','once'))&...
              ismissing(regexp(aux_titles,'(August Subsequent September)','match','once'))&...
              ~ismissing(regexp(aux_titles,'(\w+\s\w+){1}','match','once'))&...
              ismissing(regexp(aux_titles,'May|June|averaged|QI','match','once'));
                   
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

toc             
%Approximately 116 seconds
%% Write paragraphs in .mat files

Tpara    = table(Tbluebook.start_date(ind_start:ind_end),...
                 Tbluebook.end_date(ind_start:ind_end)); 

Tpara.Properties.VariableNames ...
         = {'start_date','end_date'};

for i_para = 1:size(paragraphs,2)     
   
    Tpara  = [Tpara,table(paragraphs(:,i_para))];
    
    Tpara.Properties.VariableNames{end} ...
           = strcat('Paragraph',num2str(i_para));     
end

%writetable(Tpara,'../Output/Bluebook/CSV/Paragraphs.csv');

save('../Output/Bluebook/MAT/Paragraphs.mat','Tpara'); 

%% Write paragraphs in .mat files

Tpara    = table(Tbluebook.start_date(ind_start:ind_end),...
                 Tbluebook.end_date(ind_start:ind_end)); 

Tpara.Properties.VariableNames ...
         = {'start_date','end_date'};

for i_para = 1:size(paragraphs,2)     
   
    Tpara  = [Tpara,table(paragraphs(:,i_para))];
    
    Tpara.Properties.VariableNames{end} ...
           = strcat('Paragraph',num2str(i_para));     
end

clear i_para

%writetable(Tpara,'../Output/Bluebook/CSV/Paragraphs.csv');

save('../Output/Bluebook/MAT/Paragraphs.mat','Tpara'); 

%% Write headers in .mat files

Thead    = table(Tbluebook.start_date(ind_start:ind_end),...
                 Tbluebook.end_date(ind_start:ind_end)); 

Thead.Properties.VariableNames ...
         = {'start_date','end_date'};

for i_head = 1:size(header,2)     
   
    Thead  = [Thead,table(header(:,i_head))];
    
    Thead.Properties.VariableNames{end} ...
           = strcat('Header',num2str(i_head));     
end

%writetable(Thead,'../Output/Bluebook/CSV/Headers.csv');

save('../Output/Bluebook/MAT/Header.mat','Thead'); 

%% Write header's paragraph number in .mat files

Theadnum    = table(Tbluebook.start_date(ind_start:ind_end),...
                 Tbluebook.end_date(ind_start:ind_end)); 

Theadnum.Properties.VariableNames ...
         = {'start_date','end_date'};

for i_head = 1:size(header,2)     
   
    Theadnum  = [Theadnum,table(header_indicator(:,i_head))];
    
    Theadnum.Properties.VariableNames{end} ...
           = strcat('HeaderNumber',num2str(i_head));     
end

%writetable(Theadnum,'../Output/Bluebook/CSV/HeaderParagraphNumbers.csv');

save('../Output/Bluebook/MAT/Headernum.mat','Theadnum'); 

%% Find mistakes in paragraph enumeration

aux_check_order = strtok(paragraphs);

aux_check_order  = regexp(aux_check_order,'\d{1,2}','match','once');

%% Mistakes in paragraph enumeration

tic

for i_data = 1: size(aux_check_order,1)
       
    nonmissing ...
           = string(aux_check_order(i_data,~cellfun(@isempty,aux_check_order(i_data,:))));
       
    aux_count ...
           = size(nonmissing,2); 
       
    correct_aux(i_data,1) ...
           = sum(1:1:aux_count==str2double(nonmissing),2)==aux_count;
    
end

toc

%% Generate an array with the mistakes

mistakes  = paragraphs(~correct_aux,:);

%% Write .mat file with the mistakes

Tmistakes    = table(Tpara.start_date(~correct_aux),...
                 Tpara.end_date(~correct_aux)); 

Tmistakes.Properties.VariableNames ...
         = {'start_date','end_date'};

for i_mistake = 1:size(mistakes,2)     
   
    Tmistakes  = [Tmistakes,table(mistakes(:,i_mistake))];
    
    Tmistakes.Properties.VariableNames{end} ...
           = strcat('Paragraph',num2str(i_mistake));     
end

save('../Output/Bluebook/MAT/mistakes.mat','Tmistakes'); 