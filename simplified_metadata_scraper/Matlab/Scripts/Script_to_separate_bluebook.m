%% Script to analyze bluebooks

Tbluebook   = readtable('../Output/Bluebook/CSV/bluebook_anand.csv');

%% Get the text from the file

data        = string(Tbluebook.file_text);

header      = strings(size(Tbluebook,1),1);   

%% Separate the files into blocks, according to the bluebook structure

expression  = '\(\d+\)';

for i_data      = 1:size(Tbluebook,1)

AUX         = regexp(data(i_data,:),expression,'match');    
    
[~,aux,~] = ...
             unique(AUX,'stable'); %number of listed paragraphs

%% Find the paragraphs that have a header

expression2 = 'w*[^.]\>\s+\(\d*\)';

AUX_head    = regexp(data(i_data,:),expression2,'match');

%% Select the unique numbers 

AUX         = AUX(aux);

AUX_head    = AUX_head(aux);

%% Paragraphs

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
            = aux_para(1,:);
        
    clear aux_para    
        
    end
    
end

%% Headers

headers_dummy ...
            = ~ismissing(regexpi(AUX_head,'[a-z]+','match','once'));

paragraphs_with_headers ...
            = paragraphs(i_data, headers_dummy(2:end));
               
for i_head  = 1:size(paragraphs_with_headers,2)+1
   
    if i_head == 1
        
        header(i_data,i_head) = 'Recent Developments';
       
    else 
        
        aux_split ...
            = splitSentences(paragraphs_with_headers(1,i_head-1));
        
        header(i_data,i_head)...
            = aux_split(end);
        
    end
    
end

clear aux AUX_head aux_split 
  
end

%% 

AUX(headers_dummy)
