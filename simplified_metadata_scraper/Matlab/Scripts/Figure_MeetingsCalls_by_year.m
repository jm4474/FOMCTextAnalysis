T = readtable('../../derived_data.csv');

%% Dates in standard format

T.start_dates_std_format ...
             = datetime(...
               strcat(T.start_date,{' '},string(T.year)),...
               'InputFormat','MM d yyyy');            %Start Date in standard format 
           
%% Unique Dates of Meetings and Conferences

[~,IA,~]     = unique(T.start_dates_std_format,'stable');  
                                                      %Extract unique
                                                      %meeting dates,
                                                      %ordered
                                                      %chronologically

unique_meeting_year ...
             = string(T.year(IA));                    %Year of the unique meetings

event_type   = string(T.event_type(IA));              %Type of meeting
         
%% Plot number of Meetings and Conference Calls per year

unique_years ...
             = unique(string(T.year));

Meetings_Calls ...
             = zeros(size(unique_years,1),2);
         
for t_year = 1:size(unique_years,1)
   
    dummy_year ...
           = unique_meeting_year == unique_years(t_year,1);
       
    dummy_meeting ...
           = event_type(dummy_year) =='Meeting';
       
    Meetings_Calls(t_year,:) ...
           = [sum(dummy_meeting),size(dummy_meeting,1)-sum(dummy_meeting)];
    
    clear dummy_year dummy_meeting
       
end

figure(1)

plot(1:size(unique_years,1),Meetings_Calls(:,1),'oblue','MarkerSize',3,...
    'MarkerFaceColor','b');

hold on

plot(1:size(unique_years,1),Meetings_Calls(:,2),'dred','MarkerSize',3);

hold off

xlabel('Year')

xticks(5:10:size(unique_years,1));

xticklabels(unique_years(5:10:end));

legend('FOMC Meetings','Conference Calls')

legend boxoff