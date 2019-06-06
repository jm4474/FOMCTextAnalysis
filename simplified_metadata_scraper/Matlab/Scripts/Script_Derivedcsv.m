%% Script
%  This script creates a new csv file containing 
%  a) dates in date format
%  b) dummy variable for meeting (1: meeting, 0: conference call) 
%  c) Name of document
%  d) Document "Group"
%  e) Document "Class"
%  f) Document "Type"
%  g) Document "Size"
%  h) Document "Comments"
%  The final csv excludes the following docs
%  Greenbook and Bluebook accessible materials
%  Memos
%  SEP
%  Accessible material
%  Tealbook
%  Press Conference
%  Staff statements

T = readtable('../../raw_data.csv');

dates_docs ...
  = [string(T.year),string(T.meeting_info),string(T.document_name), string(T.link)];

%% Drop some documents

dummy_GBAM ...
  = contains(dates_docs(:,3),'Greenbook and Bluebook accessible materials');
                              %Drop the ZIP files containing G/Bbook materials (19 such files)
dummy_Memos ...
  = contains(dates_docs(:,3),'Memos');
                              %Drop Memos (41 of them, available after 2003)
dummy_SEP ...
  = contains(dates_docs(:,3),'SEP');
                              %Drop SEP (22 of them, available after 2007)                                
dummy_AM ...
  = contains(dates_docs(:,3),'Accessible material');
                              %Drop AM (17 of them, available after 2007) 
                              
dummy_T ...
  = contains(dates_docs(:,3),'Tealbook');
                              %Drop Tealbooks (79 of them, available after 2010)                               

dummy_PC ...
  = contains(dates_docs(:,3),'Press Conference');
                              %Drop Press Conference (12 of them, available after 2010)
                              
dummy_SS ...
  = contains(dates_docs(:,3),'Staff statements');
                              %Drop SS (4 of them)                               
                                                            
dummy_drop ...
  =  dummy_GBAM | dummy_Memos | dummy_SEP | dummy_AM | dummy_T | dummy_PC | dummy_SS;
                              
dates_docs ...
  = dates_docs(~dummy_drop,:);      

clear dummy_GBAM  dummy_Memos  dummy_SEP  dummy_AM  dummy_T dummy_PC dummy_SS
%% Create Dates in standard format

start_dates_std_format ...
              = strings(size(dates_docs,1),1);
          
end_dates_std_format ...
              = strings(size(dates_docs,1),1);          
          
% Replace manually some problematic dates

dates_docs(strcmp(dates_docs(:,2),'April/May 30-1 Meeting - 2013'),2) ...
              = 'April 30-May 1 Meeting - 2013';
          
dates_docs(strcmp(dates_docs(:,2),'October 21, 22, 23, 26, 27, 28, 29, and 30  Conference Calls - 1987'),2) ...
              = 'October 21-October 30 Conference Calls - 1987';
          
dates_docs(strcmp(dates_docs(:,2),'October 16 (unscheduled) - 2013'),2) ...
              = 'October 16 Conference Call - 2013';        
          
%% Meetings
dummy_meeting = contains(dates_docs(:,2),'Meeting');  %1: meeting, 0: conference call

aux_dates_meeting ...
              = strcat(extractBefore(dates_docs(dummy_meeting,2),'Meeting'),'-');
                                                      %Extract Strings
                                                      %Before the word
                                                      %Meeting
start_dates_str ...
              = extractBefore(aux_dates_meeting,'-'); %Start Date in string format                                                      
                                                      
start_dates_std_format(dummy_meeting,1) ...
             = datetime(...
               join([dates_docs(dummy_meeting,1),start_dates_str]),...
               'InputFormat','yyyy MM d');            %Start Date in standard format 
           
aux_dates_meeting_2 ...
             = extractBetween(dates_docs(dummy_meeting,2),...
               start_dates_str,...
               'Meeting');                            %Extracts end date  
                                                      %(if different than start date)
           
aux_dates_meeting_2(contains(aux_dates_meeting_2,'-'))...
             = strtrim(...
               extractAfter(aux_dates_meeting_2(contains(aux_dates_meeting_2,'-')),'-')...
               );                                     %Deletes -
         
end_dates_str(strlength(aux_dates_meeting_2)>2,1) ...
             = aux_dates_meeting_2(strlength(aux_dates_meeting_2)>2); 
                                                      %Keep the dates that
                                                      %have a month
         
end_dates_str(strlength(aux_dates_meeting_2)<=2,1) ...
             = strcat( strtok(aux_dates_meeting(strlength(aux_dates_meeting_2)<=2)) , ...
               {' '}, aux_dates_meeting_2(strlength(aux_dates_meeting_2)<=2));
                                                      %Set same month
                                                     
           
end_dates_str(strlength(aux_dates_meeting_2)==0,1) ...
             = start_dates_str(strlength(aux_dates_meeting_2)==0);
                                                      %Repeat start date
         
end_dates_std_format(dummy_meeting,1) ...
             = datetime(...
               join([dates_docs(dummy_meeting,1),end_dates_str]),...
               'InputFormat','yyyy MM d');            %End Date in standard format          
         
clear aux_dates_meeting aux_dates_meeting_1 aux_dates_meeting_2 start_dates_str end_dates_str

%% Conference Calls

aux_dates_calls ...
              = strcat(extractBefore(dates_docs(~dummy_meeting,2),'Conference Call'),'-');
                                                      %Extract Strings
                                                      %Before the word
                                                      %Meeting
start_dates_str ...
              = extractBefore(aux_dates_calls,'-'); %Start Date in string format                                                      
                                                      
start_dates_std_format(~dummy_meeting,1) ...
             = datetime(...
               join([dates_docs(~dummy_meeting,1),start_dates_str]),...
               'InputFormat','yyyy MM d');            %Start Date in standard format 
           
aux_dates_calls_2 ...
             = extractBetween(dates_docs(~dummy_meeting,2),...
               start_dates_str,...
               'Conference Call');                    %Extracts end date  
                                                      %(if different than start date)
           
aux_dates_calls_2(contains(aux_dates_calls_2,'-'))...
             = strtrim(...
               extractAfter(aux_dates_calls_2(contains(aux_dates_calls_2,'-')),'-')...
               );                                     %Deletes -
         
end_dates_str(strlength(aux_dates_calls_2)>2,1) ...
             = aux_dates_calls_2(strlength(aux_dates_calls_2)>2); 
                                                      %Keep the dates that
                                                      %have a month
         
end_dates_str(strlength(aux_dates_calls_2)<=2,1) ...
             = strcat( strtok(aux_dates_calls(strlength(aux_dates_calls_2)<=2)) , ...
               {' '}, aux_dates_calls_2(strlength(aux_dates_calls_2)<=2));
                                                      %Set same month
                                                     
           
end_dates_str(strlength(aux_dates_calls_2)==0,1) ...
             = start_dates_str(strlength(aux_dates_calls_2)==0);
                                                      %Repeat start date
         
end_dates_std_format(~dummy_meeting,1) ...
             = datetime(...
               join([dates_docs(~dummy_meeting,1),end_dates_str]),...
               'InputFormat','yyyy MM d');            %End Date in standard format          
         
clear aux_dates_calls aux_dates_calls_1 aux_dates_calls_2 start_dates_str end_dates_str

%% Initialize columns for document information

name_doc = strings(size(dates_docs,1),1);   %Contains the name of the document

size_doc = strings(size(dates_docs,1),1);     %Contains the size of the document (if available)

group_doc= strings(size(dates_docs,1),1);     %Contains the class of the doccument

class_doc= strings(size(dates_docs,1),1);     %Contains the class of the doccument

file_type_doc ...
         = strings(size(dates_docs,1),1);     %File Type of the document (if available)
     
comments_doc ...
         = strings(size(dates_docs,1),1);     %Comments about the document if available
     
dummy_parent ...
         = contains(dates_docs(:,3),'('); %Dummy to check if the name has parenthesis 
     
dummy_colon ...
         = contains(dates_docs(:,3),':');     
     
dummy_PDF ...
         = contains(dates_docs(:,3),'PDF');
     
dummy_HTML ...
         = contains(dates_docs(:,3),'HTML'); 
     
dummy_MB ...
         = contains(dates_docs(:,3),'MB');       

%% Transcripts (avaiable since March 29 Meeting - 1976 to 2013)
% The most detailed record of FOMC meeting proceedings is the transcript.
 
dummy_trans ...
          = contains(dates_docs(:,3),'Transcript'); 

name_doc(dummy_trans,1) ...
          = string(repmat('Transcript',size(dates_docs(dummy_trans,1))));
      
size_doc(dummy_trans,1) ...
         = extractBefore(...
           strtrim(extractBetween(dates_docs(dummy_trans,3),'(',')')) ...
           ,'PDF');

group_doc(dummy_trans,1) ...
         = string(repmat('Transcript',size(dates_docs(dummy_trans,1))));
                     
file_type_doc(dummy_trans,1) ...
         = string(repmat('PDF',size(dates_docs(dummy_trans,1))));

clear dummy_trans     
% Presentation Materials 

dummy_PM = contains(dates_docs(:,3),'Presentation materials');

name_doc(dummy_PM,1) ...
          = string(repmat('Presentation materials',size(dates_docs(dummy_PM,1))));

size_doc(dummy_PM,1) ...
         = extractBefore(...
           strtrim(extractBetween(dates_docs(dummy_PM,3),'(',')')) ...
           ,'PDF');
       
group_doc(dummy_PM,1) ...
         = string(repmat('Transcript',size(dates_docs(dummy_PM,1))));       

file_type_doc(dummy_PM,1) ...
         = string(repmat('PDF',size(dates_docs(dummy_PM,1))));
     
clear dummy_PM

% Accessible Version

dummy_AV = contains(dates_docs(:,3),'Accessible version');

name_doc(dummy_AV,1) ...
          = string(repmat('Accessible Version',size(dates_docs(dummy_AV,1))));

size_doc(dummy_AV,1) ...
         = string(repmat('NA',size(dates_docs(dummy_AV,1))));
     
group_doc(dummy_AV,1) ...
         = string(repmat('Transcript',size(dates_docs(dummy_AV,1))));     

file_type_doc(dummy_AV,1) ...
         = string(repmat('NA',size(dates_docs(dummy_AV,1))));
     
clear dummy_AV
%% Historical Minutes (available since March 18 Meeting - 1936 to May 23 Meeting - 1967)
%  Records of attendance, discussions, decisions. Confidential until 1964.
%  In 1967 tget are split into the memoranda of discussion and Minutes of
%  actions

dummy_HM = contains(dates_docs(:,3),'Historical Minutes'); 

name_doc(dummy_HM,1) ...
         = string(repmat('Historical Minutes',size(dates_docs(dummy_HM,1))));

group_doc(dummy_HM,1) ...
         = string(repmat('Minutes',size(dates_docs(dummy_HM,1))));
     
file_type_doc(dummy_HM,1) ...
         = string(repmat('PDF',size(dates_docs(dummy_HM,1)))); 
     
size_doc(dummy_parent & dummy_HM,1) ...
         = extractBefore(...
           extractBetween(dates_docs(dummy_parent & dummy_HM,3),'(',')'),...
           'PDF');      

size_doc(~dummy_parent & dummy_HM,1) ...
         = string(repmat('NA',size(size_doc(~dummy_parent & dummy_HM,1))));  
     
comments_doc(~dummy_parent & dummy_HM,1) ...
         = extractAfter(dates_docs(~dummy_parent & dummy_HM,3),'Historical Minutes');  

clear dummy_HM     
%% Memoranda of Discussion (available since June 20 Meeting - 1967 to March 15-16 Meeting-1976)
%  It is a succcessor of the historical minutes. Contains the detailed
%  discussion that was captured in the historical minutes.

dummy_MD = contains(dates_docs(:,3),'Memoranda of Discussion'); 

name_doc(dummy_MD,1) ...
         = string(repmat('Memoranda of Discussion',size(dates_docs(dummy_MD,1))));
     
group_doc(dummy_MD,1) ...
         = string(repmat('Minutes',size(dates_docs(dummy_MD,1))));       

file_type_doc(dummy_MD,1) ...
         = string(repmat('PDF',size(dates_docs(dummy_MD,1))));     
     
size_doc(dummy_parent & dummy_MD,1) ...
         = extractBetween(dates_docs(dummy_parent & dummy_MD,3),'(',')');  
     
clear dummy_MD     
%% Minutes of Actions (available since June 20 Meeting - 1967 to December 22 Meeting - 1992)
%  Used to be part of the historical minutes. They contain a brief summary
%  of the minutes of actions, list of attendance, and actions taken. 

dummy_MA = contains(dates_docs(:,3),'Minutes of Actions'); 

name_doc(dummy_MA,1) ...
         = string(repmat('Minutes of Actions',size(dates_docs(dummy_MA,1))));
     
group_doc(dummy_MA,1) ...
         = string(repmat('Minutes',size(dates_docs(dummy_MA,1))));       

file_type_doc(dummy_MA,1) ...
         = string(repmat('PDF',size(dates_docs(dummy_MA,1))));     
     
size_doc(dummy_MA,1) ...
         = extractBetween(dates_docs(dummy_MA,3),'(',')');  
     
clear dummy_MA     
%% Record of Policy Actions (avaiable since March 29 Meeting - 1976 to December 22 Meeting - 1992) 
%Available since 1936. Before 1967 this is the only document written for public release. 

dummy_ROPA = contains(dates_docs(:,3),'Record of Policy Actions'); 

name_doc(dummy_ROPA,1) ...
         = string(repmat('Record of Policy Actions',size(dates_docs(dummy_ROPA,1))));
     
group_doc(dummy_ROPA,1) ...
         = string(repmat('Minutes',size(dates_docs(dummy_ROPA,1))));       

file_type_doc(dummy_ROPA,1) ...
         = string(repmat('PDF',size(dates_docs(dummy_ROPA,1))));     
     
size_doc(dummy_parent & dummy_ROPA,1) ...
         = extractBefore(...
           extractBetween(dates_docs(dummy_parent & dummy_ROPA,3),'(',')'),...
           'PDF');  
     
size_doc(~dummy_parent & dummy_ROPA,1) ...
         = string(repmat('NA',size(size_doc(~dummy_parent & dummy_ROPA,1))));  
          
comments_doc(~dummy_parent & dummy_ROPA,1) ...
         = extractAfter(dates_docs(~dummy_parent & dummy_ROPA,3),':');           
%% Minutes (available since February 2-3 Meeting-1993 to present)     

dummy_MA = contains(dates_docs(:,3),'Minutes of Actions'); 

dummy_IEM = contains(dates_docs(:,3),'Intermeeting Executive Committee Minutes'); 

dummy_HM = contains(dates_docs(:,3),'Historical Minutes'); 

dummy_M = contains(dates_docs(:,3),'Minutes') & ~dummy_MA & ~dummy_IEM & ~dummy_HM; 

name_doc(dummy_M,1) ...
         = string(repmat('Minutes',size(dates_docs(dummy_M,1))));
     
group_doc(dummy_M,1) ...
         = string(repmat('Minutes',size(dates_docs(dummy_M,1))));      
     
file_type_doc(dummy_M & dummy_PDF,1) ...
         = string(repmat('PDF',size(dates_docs(dummy_M & dummy_PDF,1))));
     
file_type_doc(dummy_M & dummy_HTML,1) ...
         = string(repmat('HTML',size(dates_docs(dummy_M & dummy_HTML,1))));  
     
file_type_doc(dummy_M & ~dummy_HTML & ~dummy_PDF ,1) ...
         = string(repmat('PDF',size(dates_docs(dummy_M & ~dummy_HTML & ~dummy_PDF,1))));  
     
size_doc(dummy_M & dummy_PDF,1) ...
         = extractBetween(dates_docs(dummy_M & dummy_PDF,3),':','PDF'); 
     
comments_doc(dummy_parent & dummy_M,1) ...
         = extractBetween(dates_docs(dummy_parent & dummy_M,3),'(',')');
     
comments_doc(~dummy_parent & dummy_colon & dummy_M,1) ...
         = extractAfter(dates_docs(~dummy_parent & dummy_colon & dummy_M,3),':');    
     
clear  dummy_MA  dummy_IEM dummy_HM dummy_M  
%% Bluebook (available since November 2 Meeting-1965 to present)

dummy_blue = contains(dates_docs(:,3),'Bluebook');

name_doc(dummy_blue,1) ...
          = string(repmat('Bluebook',size(dates_docs(dummy_blue,1))));
      
size_doc(dummy_blue,1) ...
         = extractBefore(...
           strtrim(extractBetween(dates_docs(dummy_blue,3),'(',')')) ...
           ,'PDF');   
       
group_doc(dummy_blue,1) ...
         = string(repmat('Bluebook',size(dates_docs(dummy_blue,1))));
                     
file_type_doc(dummy_blue,1) ...
         = string(repmat('PDF',size(dates_docs(dummy_blue,1))));  
     
clear dummy_blue    
%% Only Greenbook (avaiable since June 17 Meeting-1964 to July 16-1974)
dummy_green = contains(dates_docs(:,3),'Greenbook');

dummy_part1 = contains(dates_docs(:,3),'Part 1');

dummy_part2 = contains(dates_docs(:,3),'Part 2');

dummy_Sup = contains(dates_docs(:,3),'Supplement');

dummy_only_green ...
          = dummy_green & ~dummy_part1 & ~dummy_part2 & ~dummy_Sup;

name_doc(dummy_only_green,1) ...
          = string(repmat('Greenbook',size(dates_docs(dummy_only_green,1))));
      
size_doc(dummy_only_green,1) ...
         = extractBefore(...
           strtrim(extractBetween(dates_docs(dummy_only_green,3),'(',')')) ...
           ,'PDF');   
       
group_doc(dummy_only_green,1) ...
         = string(repmat('Greenbook',size(dates_docs(dummy_only_green,1))));
                     
file_type_doc(dummy_only_green,1) ...
         = string(repmat('PDF',size(dates_docs(dummy_only_green,1))));  
     
clear dummy_only_green    
%% Part 1-2-Sup Greenbook (avaiable since August 20-Meeting 1974 to April 27-28 Meeting 2010)
% Part 1: Current Economic and Financial Conditions: Summary and Outlook

dummy_all_green ...
            = dummy_green & (dummy_part1 | dummy_part2 | dummy_Sup);

name_doc(dummy_all_green,1) ...
          = strtrim(extractBefore(...
           strtrim(extractAfter(dates_docs(dummy_all_green,3),':')) ...
           ,'('));  
      
size_doc(dummy_all_green,1) ...
         = extractBefore(...
           strtrim(extractBetween(dates_docs(dummy_all_green,3),'(',')')) ...
           ,'PDF');   
       
group_doc(dummy_all_green,1) ...
         = string(repmat('Greenbook',size(dates_docs(dummy_all_green,1))));
                     
file_type_doc(dummy_all_green,1) ...
         = string(repmat('PDF',size(dates_docs(dummy_all_green,1))));  
     
clear dummy_all_green dummy_part1 dummy_part2 
%% Supplement Greenbook

dummy_supp = contains(dates_docs(:,3),'Supplement') & ~dummy_green;

name_doc(dummy_supp,1) ...
          = string(repmat('Supplement',size(dates_docs(dummy_supp,1))));
      
size_doc(dummy_supp,1) ...
         = extractBefore(...
           strtrim(extractBetween(dates_docs(dummy_supp,3),'(',')')) ...
           ,'PDF');   
       
group_doc(dummy_supp,1) ...
         = string(repmat('Greenbook',size(dates_docs(dummy_supp,1))));
                     
file_type_doc(dummy_supp,1) ...
         = string(repmat('PDF',size(dates_docs(dummy_supp,1))));  

clear dummy_supp dummy_green   
%% Beigebook (available since July 12-12 Meeting 1983 to present)
% Summary of Commentary on Current Economic Conditions by Federal Reserve District.

dummy_beige = contains(dates_docs(:,3),'Beige Book');

name_doc(dummy_beige,1) ...
          = string(repmat('Beige Book',size(dates_docs(dummy_beige,1))));
      
group_doc(dummy_beige,1) ...
         = string(repmat('Beige Book',size(dates_docs(dummy_beige,1)))); 
     
file_type_doc(dummy_beige,1) ...
         = string(repmat('PDF',size(dates_docs(dummy_beige,1)))); 
     
file_type_doc(dummy_beige & dummy_HTML,1) ...
         = string(repmat('HTML',size(dates_docs(dummy_beige & dummy_HTML ,1)))); 
     
size_doc(dummy_beige & dummy_MB,1) ...
         = strtrim(extractBetween(dates_docs(dummy_beige & dummy_MB,3),':','PDF'));

clear dummy_beige     
%% Redbook (available since May 26-1970 Meeting to May 24 Meeting 1983 )

dummy_red = contains(dates_docs(:,3),'Redbook');

name_doc(dummy_red,1) ...
          = string(repmat('Redbook',size(dates_docs(dummy_red,1))));
      
size_doc(dummy_red,1) ...
         = extractBefore(...
           strtrim(extractBetween(dates_docs(dummy_red,3),'(',')')) ...
           ,'PDF');   
       
group_doc(dummy_red,1) ...
         = string(repmat('Beige Book',size(dates_docs(dummy_red,1))));
                     
file_type_doc(dummy_red,1) ...
         = string(repmat('PDF',size(dates_docs(dummy_red,1))));  
     
clear dummy_red  
%% Agenda  (available since January 7th-1964 Meeting to present)

dummy_agenda = contains(dates_docs(:,3),'Agenda');

name_doc(dummy_agenda,1) ...
          = string(repmat('Agenda',size(dates_docs(dummy_agenda,1))));
      
size_doc(dummy_agenda,1) ...
         = extractBefore(...
           strtrim(extractBetween(dates_docs(dummy_agenda,3),'(',')')) ...
           ,'PDF');   
       
group_doc(dummy_agenda,1) ...
         = string(repmat('Agenda',size(dates_docs(dummy_agenda,1))));
                     
file_type_doc(dummy_agenda,1) ...
         = string(repmat('PDF',size(dates_docs(dummy_agenda,1))));  
     
clear dummy_agenda    
%% Statement (available since January -1994 Meeting to present)
%The FOMC first announced the outcome of a meeting in February 1994.
% After making several further post-meeting statements in 1994, 
% the Committee formally announced in February 1995 that all changes in the stance of 
% monetary policy would be immediately communicated to the public. 
% In January 2000, the Committee announced that it would issue a statement following 
% each regularly scheduled meeting, regardless of whether there had been a 
% change in monetary policy.

dummy_statement = contains(dates_docs(:,3),'Statement');

name_doc(dummy_statement,1) ...
          = string(repmat('Statement',size(dates_docs(dummy_statement,1))));
       
group_doc(dummy_statement,1) ...
         = string(repmat('Statement',size(dates_docs(dummy_statement,1))));
                     
file_type_doc(dummy_statement,1) ...
         = string(repmat('HTML',size(dates_docs(dummy_statement,1))));  
     
clear dummy_statement 
%% Intermeeting Executive Committee Minutes

dummy_IEM = contains(dates_docs(:,3),'Intermeeting Executive Committee Minutes');

name_doc(dummy_IEM,1) ...
          = string(repmat('IMECM',size(dates_docs(dummy_IEM,1))));
      
size_doc(dummy_IEM,1) ...
         = extractBefore(...
           strtrim(extractBetween(dates_docs(dummy_IEM,3),'(',')')) ...
           ,'PDF');   
       
group_doc(dummy_IEM,1) ...
         = string(repmat('Minutes',size(dates_docs(dummy_IEM,1))));
                     
file_type_doc(dummy_IEM,1) ...
         = string(repmat('PDF',size(dates_docs(dummy_IEM,1))));  
     
clear dummy_IEM
%% Generate Class

class_doc(:,1) = 'Economic Information';

class_doc(strcmp(group_doc,'Transcript'),1) ...
         ='Transcript';
     
class_doc(strcmp(group_doc,'Agenda'),1) ...
         ='Agenda';     

class_doc(strcmp(group_doc,'Statement')|strcmp(group_doc,'Minutes'),1) ...
         ='Meeting Summary';
%% Write CSV file

T_derived  ...
     = table(dates_docs(:,1),dates_docs(:,2),dates_docs(:,3),dates_docs(:,4),... %original
             start_dates_std_format,end_dates_std_format,...                     %dates
             dummy_meeting,...
             name_doc,group_doc,class_doc,size_doc,file_type_doc,comments_doc);

T_derived.Properties.VariableNames ...
     = {'Year','Dates','Documents','Links'...
         'StartDate','EndDate'...
          'DummyMeeting',...
          'Name','Group','Class','Size','FileType','Comments'};

writetable(T_derived,'../Output/FedCorpus_derived.xls');

clearvars -except T_derived