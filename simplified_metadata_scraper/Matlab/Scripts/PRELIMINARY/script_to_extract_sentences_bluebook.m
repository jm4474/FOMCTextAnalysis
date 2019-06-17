%% Scripts to isolate sentences in relevant paragraphs

load('../Output/Bluebook/MAT/Paragraphs.mat'); %

%% Convert table to string array

Paragraphs = table2array(Tpara(:,3:end));   %Matrix containing the different paragraphs for each meeting

%% Define regular Expression and look for alternatives

expression = '([Aa]lternative\s+[AaBbCcDdEe])';

aux        = regexp(Paragraphs,expression,'match'); 
                                            %Cell Indicating the number of
                                            %paragraphs that contain the
                                            %regular expression

%% Look for alternative A B C D

alternativeA = strings(size(aux,1),1);

numberofsentences_altA ...
             = zeros(size(aux,1),1);
         
alternativeB = strings(size(aux,1),1);

numberofsentences_altB ...
             = zeros(size(aux,1),1);         

alternativeC = strings(size(aux,1),1);

numberofsentences_altC ...
             = zeros(size(aux,1),1);  
         
alternativeD = strings(size(aux,1),1);

numberofsentences_altD ...
             = zeros(size(aux,1),1);           
         
tic         
         
for i_data = 1:size(aux,1)

aux(i_data,~cellfun(@isempty,aux(i_data,:)));

relevant_paragraphs ...
     = Paragraphs(i_data,~cellfun(@isempty,aux(i_data,:)));

if isempty(relevant_paragraphs)

alternativeA(i_data,:) = 'No Sentences Alternative A';    
    
alternativeB(i_data,:) = 'No Sentences Alternative B';   

alternativeC(i_data,:) = 'No Sentences Alternative C'; 

alternativeD(i_data,:) = 'No Sentences Alternative D';  

else    
    
aux_sentences ...
     = splitSentences(join(relevant_paragraphs,'.'));

expressionA ...
     = '[Aa]lternative\s+[Aa][^a-z]';
 
expressionB ...
     = '[Aa]lternative\s+[Bb][^a-z]'; 
 
expressionC ...
     = '[Aa]lternative\s+[Cc][^a-z]'; 
 
expressionD ...
     = '[Aa]lternative\s+[Dd][^a-z]';   
 
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
 
end 

end

toc

clear sentencesA sentencesB sentencesC sentencesD relavant_paragraphs

%% Connect to the summary table

Tsummary = readtable('../Output/Bluebook/CSV/TableSummary.csv');

Tsummary = [Tsummary,table(alternativeA),table(numberofsentences_altA)...
            table(alternativeB),table(numberofsentences_altB),...
            table(alternativeC),table(numberofsentences_altC),...
            table(alternativeD),table(numberofsentences_altD)];
        
writetable(Tsummary,'../Output/Bluebook/CSV/TableSummary_sentencecount.csv');         
        
%% Plot


listofmembers = string(['Alternative A' ; 'Alternative B' ; 'Alternative C' ; 'Alternative D' ]);

num_members   = size(listofmembers, 1);

% Take attendence

attendence    = double([numberofsentences_altA>0,...
                 numberofsentences_altB>0,...
                 numberofsentences_altC>0,...
                 numberofsentences_altD>0]);
                  
[listofmembers, aux_ind]        ...
              = sort(listofmembers,'ascend'); 
          
attendence_edited ...
              = attendence(:,aux_ind);
          
%% Plot alternatives discussed

% Find kmax most often members
kmax            = 4;

%[~, koftenmeet] = maxk(sum(attendence_edited, 1), kmax);

kmaxlist        = listofmembers;

kmaxattendence = attendence_edited;

% Plot members

figure('Name', 'Alternatives') 

for i = 1:kmax
    
   scatter(Tsummary.start_date, i * kmaxattendence(:, i), 'filled')
   
    hold on;
    
end

% Change ylim

ylim([.5, kmax + 0.5])

% Put labels

yticks(1:kmax)

yticklabels(kmaxlist)

% Horizontal  
y1 = get(gca,'ylim');

trans_date = datetime('19931116', 'InputFormat', 'yyyyMMdd'); % transparency meeting in datetime

plot([trans_date, trans_date], y1, '--', ...
'Color', 'black','LineWidth', 1, 'HandleVisibility','off')
