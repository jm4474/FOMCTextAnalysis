%% Scripts count number of paragraphs containing alternatives

load('../Output/Bluebook/MAT/Paragraphs.mat'); %

%% Convert table to string array

Paragraphs = table2array(Tpara(:,3:end));   %Matrix containing the different paragraphs for each meeting

%% Define regular Expression and look for alternatives

expression = '([Aa]lternative\s+[AaBbCcDdEe])';

aux        = regexp(Paragraphs,expression,'match'); 
                                            %Cell Indicating the number of
                                            %paragraphs that contain the
                                            %regular expression

%% Obtain the alternatives discussed in each meeting and the paragraphs containing the discussion

tic

alternatives_discussed = strings(size(Paragraphs,1),1);  %Collect the alternatives discussed

alternatives_parags    = strings(size(Paragraphs,1),1);  %Collect the number of paragraphs

for i_data = 1:size(Paragraphs,1)

alt_meeting = aux(i_data,~cellfun(@isempty,aux(i_data,:)));

alt_parags  = Paragraphs(i_data,~cellfun(@isempty,aux(i_data,:)));

if isempty(alt_meeting)

alternatives_discussed(i_data,1) = 'No alternatives found';     

alternatives_parags(i_data,1)    = 'No alternatives found';

else

alternatives_parags(i_data,1)    =  join(strtok(Paragraphs(i_data,~cellfun(@isempty,aux(i_data,:)))),...
                                    ', ');   
    
list_meeting ...
            = alt_meeting{1};    %Alternatives discussed in the first nonempty paragraph of the meeting

                                 %The following lines are just used to
                                 %put the alternatives found in a common
                                 %format
        
list_meeting ...
            = regexprep(list_meeting, '[Aa]lternative\s+[Aa]','Alternative A');
        
   list_meeting ...
            = regexprep(list_meeting, '[Aa]lternative\s+[Bb]','Alternative B');
        
   list_meeting ...
            = regexprep(list_meeting, '[Aa]lternative\s+[Cc]','Alternative C');
        
   list_meeting ...
            = regexprep(list_meeting, '[Aa]lternative\s+[Dd]','Alternative D');           
        
   list_meeting ...
            = regexprep(list_meeting, '[Aa]lternative\s+[Ee]','Alternative E');
        
for i_alt   = 1: size(alt_meeting,2)-1

   list_meeting ...
            = [list_meeting , alt_meeting{1,i_alt+1}];
        
   list_meeting ...
            = regexprep(list_meeting, '[Aa]lternative\s+[Aa]','Alternative A');
        
   list_meeting ...
            = regexprep(list_meeting, '[Aa]lternative\s+[Bb]','Alternative B');
        
   list_meeting ...
            = regexprep(list_meeting, '[Aa]lternative\s+[Cc]','Alternative C');
        
   list_meeting ...
            = regexprep(list_meeting, '[Aa]lternative\s+[Dd]','Alternative D');     
        
end

alternatives_discussed(i_data,1) = join(unique(list_meeting),', '); 
                                                           
end

end

toc

%% Number of total blocks of paragraphs per meeting

dummyemptypara ...
           = ~cellfun(@isempty,Paragraphs);

TotalParagraphs ...
           = sum(dummyemptypara,2);

%% Number of relevant paragraphs for each meeting

dummyemptyrelevant ...
           = ~cellfun(@isempty,aux);

TotalRelevantParagraphs...
           = sum(dummyemptyrelevant,2); 

%% Create a table that contain dates, number of paragraphs and alternatives discussed

TSummary   = [Tpara(:,1:2),...
              table(TotalParagraphs),...
              table(TotalRelevantParagraphs),...
              table(alternatives_discussed),table(alternatives_parags)];

clear i_data i_alt list_meeting alt_parags alt_meeting          
          
%%  Write CSV file

writetable(TSummary,'../Output/Bluebook/CSV/TableSummary.csv')

%%
          
%TFEDFUNDS=readtable('../Data/FEDFUNDS.xls');

%datesfedfunds=string(datestr(TFEDFUNDS.observation_date(:,1),'yyyy-mm-dd'));

