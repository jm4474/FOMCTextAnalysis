%% Script to Download Bluebooks

T = readtable('../../../derived_data.csv');%This table contains information regarding 
                                           %the documents available for
                                           %each meeting/conference call
                                           %since 1936.
%% Eliminate extra spaces

T.file_name = strtrim(T.file_name);        %Remove extra spaces in the file_name

T.grouping = strtrim(T.grouping);          %Remove extra spaces in the file_type

%% Download the bluebooks and save them
tic

options ...
     = weboptions;
 
weboptions.Timeout ...
     = 15;

for t_bbook = 1:size(Tbluebook,1)

websave(strcat('../../Output/Bluebook/bluebook',num2str(t_bbook),'.pdf'),string(Tbluebook.link(t_bbook))...
        ,options);
    
end

toc