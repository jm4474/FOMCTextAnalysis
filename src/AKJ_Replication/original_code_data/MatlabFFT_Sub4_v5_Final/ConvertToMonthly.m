function [MonthData,MonthColHead,data] = ConvertToMonthly(data,colheaders,Start,End)

%if the data for the policy model are at daily frequency -> convert to
%monthly by using data at the end of prior month as predictors for current
%month policy if there is no scheduled meeting. If there is a scheduled
%meeting, use day before meeting announcemnt as predictor for outcome of
%meeting.
%For changes outside of scheduled meetings use information at end of prior
%month as predictor.
%If there are more than one target rate change within a month, the changes
%are cumulated. Price information is collected prior to first announced
%meeting or end of last month if no announced meeting.
%Date Stamp on monthly data indicates calander day on which FFF prices were
%recorded - NOT the day when target rate was changed. 

%Restrictions: the daily data set is assumed to start on the last day of a
%month and is assumed to have no meetings on last two days in the sample


%The algorithm searches  throug the daly data in two nested loops. The
%outerloop (i) goes through data at the monthly level (skips from month to
%month, the inner loop (j) starts at the beginning of the month and scans
%forward to the end of the month. During the scan, the algorithm searches
%for changes in the Target rate. It records changes during scheduled
%meetings in 'currentData' and changes outside of scheduled meetings in
%'currDatNoFO'. Once the end of the month is reached, the routine
%AccountMonth is called. In that routine the monthly database is built. It
%contains the year and month stamp for the monthly data, date of first and
%if present second schedule FOMC meeting, date of any change outside of
%scheduled FOMC meeting, date of closest date that can be used for
%prediction and rate data corresponding to that date. 

%The routine GenSurprise uses this information to
%form the variables FCyear, FCmonth, FCday

% The routine adds the following timing information:
% 'DataYear' year of policy shock for monthly time series
% 'DataMonth' month of policy shock for monthly time series
% 'ChangeYear' Exact date when target rate change occurred
% 'ChangeMonth' Exact date when target rate change occurred
% 'ChangeDay' Exact date when target rate change occurred
% '2ndChangeYear' Exact date when 2nd target rate change occurred
% '2ndChangeMonth' Exact date when 2nd target rate change occurred
% '2ndChangeDay' Exact date when 2nd target rate change occurred
% 'NoFOMCYear' Exact Date when change outside of FOMC occurred
% 'NoFOMCMonth' Exact Date when change outside of FOMC occurred
% 'NoFOMCDay' Exact Date when change outside of FOMC occurred
% DYear, DMonth, DDate: Exact date of daily data for which Interest rate
% data was used. The data in this file are suitable to be used in the
% p-score directly, because they predate the policy announcement.

colFFF0      = strcmp(colheaders,'FFF0');
colFFF1      = strcmp(colheaders,'FFF1');
dataFFF      = [data(:,colFFF0) data(:,colFFF1)];

dataFFF         = fillforward(dataFFF);          % Outcome data
data(:,colFFF0) = dataFFF(:,1);
data(:,colFFF1) = dataFFF(:,2);
year         = data(:,strcmp(colheaders,'Year'));
month        = data(:,strcmp(colheaders,'Month'));
day          = data(:,strcmp(colheaders,'Day'));
if isempty(day)
    day          = eomday(year,month);
end

End          = datenum(End);
Start        = datenum(Start);
dy           = datenum(year,month,day);
ind          = ((dy>=Start & dy<=End));
dy           = dy(ind);
data         = data(ind,:); %Select data between Start and End
% Reset Year Month and Day for restricted Dataset
year         = data(:,strcmp(colheaders,'Year'));
month        = data(:,strcmp(colheaders,'Month'));
day          = data(:,strcmp(colheaders,'Day')); 

%Find last day of each month

FOMC         = data(:,strcmp(colheaders,'FOMC Meetings'));
FOMCData     = data((FOMC==1),:);
FOMCyear     = FOMCData(:,strcmp(colheaders,'Year'));
FOMCmonth    = FOMCData(:,strcmp(colheaders,'Month'));
FOMCday      = FOMCData(:,strcmp(colheaders,'Day'));

FOMCdy       = datenum(FOMCyear,FOMCmonth,FOMCday);
e1           = ones(length(FOMCdy),1);
prevMon      = 0;
MonthData    = [];

colChange    = strcmp(colheaders,'Change');
outChange    = strcmp(colheaders,'Indicates Changes Outside FOMC');
colFOMC      = strcmp(colheaders,'FOMC Meetings');
colQE        = strcmp(colheaders,'qe');
colTR        = strcmp(colheaders,'Target Rate');
TargetRate   = [];
cDOld        = [];
currentData  = [];
currDatNoFO  = []; %store change during month if occurred outside of FOMC
i            = 2;
while i<=length(data)-2;
    [~,CM,~] = datevec(dy(i));
    if CM ~= prevMon
    %New Month
    %Set number of meetings in current month to zero
    MeetingNum  = 0;  %number of scheduled meetings in month
    if ~isempty(currentData)
        cDOld   = currentData;
        currentData = [];        
    end
    currDatNoFO = []; %clear date of change outside FOMC
    MonthChange = 0;  %total change of target rate in month (scheduled and unscheduled)     
    MonthQE     = 0;  %QE announcement in month (scheduled and unscheduled)     
    MeetFlag    = false;   
    outChangeFlag = false;
    j           = i;
        while ((month(j) == CM) && (j< length(data)));
            %check if meeting in current month
            if ~isempty(find(dy(j)*e1==FOMCdy,1));
            %there is a meeting in this month
                MeetFlag   = true;
                MeetingNum = MeetingNum+1;
                if MeetingNum == 1
                   %found first meeting of month, does not start on last
                   %day of month
                    if ~isempty(find(dy(j+1)*e1==FOMCdy,1)); %meeting is two days
                        %check if meeting lasts two days
                        if j<length(data)-2
                            if month(j+1)~=CM || (month(j+2)~=CM && data(j+2,colChange)~=0) 
                               % if change falls on new month, save data for previous month and re-initialize 
                               MonthData = AccountMonth(MonthData,currentData,currDatNoFO,MonthChange,MonthQE,...
                                   MeetingNum-1,outChangeFlag,outChange,colChange,colQE,colFOMC,data,i);
                               currentData = [];
                               MonthChange = 0;
                               MonthQE     = 0;
                               CM = month(j+2); %meeting started in previous month but counts towards next month
                            end    
                        end
                        if (year(j)>=1995 || (year(j)>=1994 && month(j)>=2) || (year(j)==1990 && month(j)==12))
                            %if rate change occurred on same day as meeting
                            MonthChange = MonthChange + data(j+1,colChange);
                            if ~isempty(colQE)
                                MonthQE      = MonthQE +data(j+1,colQE);
                            end
                            currentData = [zeros(1,6), data(j,:)];
                            %if meeting is two days, use information at market
                            %close of first day of meeting; note that
                            %data(j,1:3) contain the calendar date at
                            %position j. This calendar date is used as the
                            %timing for the predictor variable used in the
                            %p-score

                            currentData(1,1) = year(j+1); %record month of rate change
                            currentData(1,2) = month(j+1);
                            currentData(1,3) = day(j+1);
                        else
                            MonthChange = MonthChange + data(j+2,colChange);
                            if ~isempty(colQE)
                                MonthQE      = MonthQE +data(j+2,colQE);
                            end                                                        
                            currentData = [zeros(1,6), data(j+1,:)];
                            %pre 1994 use info at close of second day of
                            %meeting, here closest predictor variable
                            %allowed is at the end of the second day of the
                            %meeting.
                            currentData(1,1) = year(j+2); %record month of rate change
                            currentData(1,2) = month(j+2);  
                            currentData(1,3) = day(j+2);
                             %change in FFR occurs two days after meeting starts
                        end
                        j = j + 2; %skip to first day after meeting
                    else  %meeting only one day long
                        if j<length(data)-2;
                            if (month(j+1)~=CM ) && data(j+1,colChange)~=0 ||...
                                    (~(year(j)>1995 || (year(j)>=1994 && month(j)>=2)) && (month(j+1)~=CM ))
                                % meeting is one day and falls at end of month
                               MonthData = AccountMonth(MonthData,currentData,currDatNoFO,MonthChange,MonthQE,...
                                   MeetingNum,outChangeFlag,outChange,colChange,colQE,colFOMC,data,i);
                               currentData = [];
                               MonthChange = 0;                          
                               MonthQE     = 0;
                               CM = month(j+1); %meeting started in previous month but counts towards next month                           
                            end                 
                        end
                        if (year(j)>1995 || (year(j)>=1994 && month(j)>=2))
                           %if rate change occurred on same day as meeting 
                           MonthChange = MonthChange +  data(j,colChange);    
                           if ~isempty(colQE)
                                MonthQE      = MonthQE +data(j,colQE);
                           end
                           currentData = [zeros(1,6), data(j-1,:)];
                            %if meeting is one day, and post 1994 use info
                            %on closing of day before meeting

                           currentData(1,1) = year(j); %record month of rate change
                           currentData(1,2) = month(j);
                           currentData(1,3) = day(j);
                        else
                            MonthChange = MonthChange +  data(j+1,colChange);
                            if ~isempty(colQE)
                                MonthQE      = MonthQE +data(j,colQE);
                            end
                            currentData = [zeros(1,6), data(j,:)];
                            %if meeting is one day, and prior 1994 use info
                            %on closing of day of meeting (announcement to
                            %public is made the next day)

                            currentData(1,1) = year(j+1); %record month of rate change
                            currentData(1,2) = month(j+1);     
                            currentData(1,3) = day(j+1);
                        end
                        %change in FFR occurs one day after meeting starts
                        j = j + 1; %skip to first day after meeting
                    end
                elseif MeetingNum > 1
                   %found additional scheduled meetings, do not start at
                   %last day of month
                   if ~isempty(find(dy(j+1)*e1==FOMCdy,1));
                        %check if meeting last two days
                        %keep information prior to first meeting of month                      
                        if j<=length(data)-2
                            if month(j+1)~=CM || (month(j+2)~=CM && data(j+2,colChange)~=0)
                               MonthData = AccountMonth(MonthData,currentData,currDatNoFO,...
                                   MonthChange,MonthQE,MeetingNum,outChangeFlag,outChange,colChange,colQE,colFOMC,data,i);
                               currentData = [];
                               MonthChange = 0;                           
                               MonthQE     = 0;
                               CM = month(j+2); %meeting started in previous month but counts towards next month                           
                            end         
                        end
                        if (year(j)>1995 || (year(j)>=1994 && month(j)>=2))  
                            %if rate change occurred on same day as meeting
                            %keep information prior to first meeting of month       
                            %note currentData(:,7:end) does not change because
                            %first available predictor is related to first
                            %meeting in the month
                            
                            MonthChange = MonthChange + data(j+1,colChange);
                            if ~isempty(colQE)
                                MonthQE      = MonthQE +data(j+1,colQE);
                            end
                            currentData(1,4) = year(j+1); %record month of rate change
                            currentData(1,5) = month(j+1);
                            currentData(1,6) = day(j+1);
                        else
                            MonthChange = MonthChange + data(j+2,colChange);
                            if ~isempty(colQE)
                                MonthQE      = MonthQE +data(j+2,colQE);
                            end                           
                            %change in FFR occurs two days after meeting starts
                            %cumulate change over entire month   
                            currentData(1,4) = year(j+2); %record month of rate change
                            currentData(1,5) = month(j+2);
                            currentData(1,6) = day(j+2);
                        end
          
                        j = j + 2; %skip to first day after meeting
                    else                  
                        %if meeting is one day,
                        %keep information prior to first meeting of month       
                        %note currentData(:,7:end) does not change because
                        %first available predictor is related to first
                        %meeting in the month
                        if j<length(data)-2
                            if (month(j+1)~=CM && data(j+1,colChange)~=0)
                               MonthData = AccountMonth(MonthData,currentData,currDatNoFO,...
                                   MonthChange,MonthQE,MeetingNum,outChangeFlag,outChange,colChange,colQE,colFOMC,data,i);
                               currentData = [];
                               MonthChange = 0;
                               MonthQE     = 0;
                               CM = month(j+1); %meeting started in previous month but counts towards next month                           
                            end            
                        end
                        if (year(j)>=1995 || (year(j)>=1994 && month(j)>=2) || (year(j)==1990 && month(j)==12))
                           %if rate change occurred on same day as meeting 
                           MonthChange = MonthChange +  data(j,colChange);
                           if ~isempty(colQE)
                                MonthQE      = MonthQE +data(j,colQE);
                           end                           
                           currentData(1,4) = year(j); %record month of rate change
                           currentData(1,5) = month(j);
                           currentData(1,6) = day(j);
                        else
                           MonthChange = MonthChange +  data(j+1,colChange);
                           if ~isempty(colQE)
                                MonthQE      = MonthQE +data(j+1,colQE);
                           end                           
                           %change in FFR occurs one day after meeting starts
                           
                           currentData(1,4) = year(j+1); %record month of rate change
                           currentData(1,5) = month(j+1);
                           currentData(1,6) = day(j+1);
                        end
                         j = j + 1; %skip to first day after meeting
                   end
                end
            end
            if data(j,outChange) == 1 && ~MeetFlag %unscheduled meeting
                MonthChange = MonthChange + data(j,colChange);                
                outChangeFlag = true;
                if isempty(currDatNoFO)
                    %record date of change outside of FOMC
                    currDatNoFO(1,1) = year(j);
                    currDatNoFO(1,2) = month(j);
                    currDatNoFO(1,3) = day(j); 
                else
                    % if there already was a change outside FOMC do nothing
                    % i.e. keep date of first change.
                end
            end
            if ~isempty(find(colQE==1,1))
                if data(j,colQE) == 1 && ~MeetFlag
                    if ~isempty(colQE)
                          MonthQE      = MonthQE +data(j,colQE);
                    end
                    outChangeFlag = true;
                end
            end
            j = j + 1;
            %check if meeting overlaps end of month
            MeetFlag = false;
        end
        MonthData = AccountMonth(MonthData,currentData,currDatNoFO,MonthChange,MonthQE,...
                MeetingNum,outChangeFlag,outChange,colChange,colQE,colFOMC,data,i);        
    end
    if j == length(data)
        i = j+1; %terminate
    else
        i = j; %skip to beginning of new month
    end
    TargetRate  = [TargetRate;data(i-1,colTR)];
    prevMon = CM;    
end
%The variables DYear, DMonth, DDay contain the date for the prediction
%variable closest to the meeting, or if there is no meeting for the
%corresponding month (DataYear,DataMonth) then the date is the last month
%prior to the Datamonth. Similarly, if there was a meeting but a change
%outside a meeting occurred prior to the first meeting, prediction
%information at the end of the month prior is used (example August 1991)

colheaders(1,1) = cellstr('DYear');
colheaders(1,2) = cellstr('DMonth');
colheaders(1,3) = cellstr('DDay');
MonthColHead = ['Year','Month','ChangeYear','ChangeMonth','ChangeDay',...
                '2ndChangeYear','2ndChangeMonth','2ndChangeDay',...
                'NoFOMCYear','NoFOMCMonth','NoFOMCDay','DNoFOMC',colheaders];

        
        