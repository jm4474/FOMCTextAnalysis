function MonthData = AccountMonth(MonthData,currentData,currDatNoFO,MonthChange,MonthQE,MeetingNum,outChangeFlag,outChange,colChange,colQE,colFOMC,data,i)
% function records monthly aggregate data from search over daily rate;
% search result is stored in currentData which contains timing of FOMC
% meetings, closest possible predictor date and rate information;
% currDatNoFO contains the date of a change that occurred outside of FOMC
% meetings. If it predates the first change at a meeting, information at
% the end of the previous month is used as the predictor - If not,
% information the day before the frist scheduled FOMC meeting is used. 

% changes
        if isempty(currentData) && isempty(currDatNoFO)
           %no meeting scheduled in month, no change outside of FOMC use information from last day of
           %prior month, set change to zero.
           currentData = [data(i,1:2),zeros(1,10),data(i-1,:)];
           currentData(1,[false(1,12),colChange]) = MonthChange; %offset +2 needed because additional date info added in previous line
           if MonthQE == 0
              currentData(1,[false(1,12),colQE]) = MonthQE;
           else
              currentData(1,[false(1,12),colQE]) = 1;  % if more then one QE announcement per month then only report one.
           end
        elseif isempty(currentData) && ~isempty(currDatNoFO)
           %no meeting scheduled in month, but change outside of FOMC use information from last day of
           %prior month, set change to zero.
           currentData = [data(i,1:2),zeros(1,6),currDatNoFO,zeros(1,1),data(i-1,:)];
           currentData(1,[false(1,12),colChange]) = MonthChange; %offset +2 needed because additional date info added in previous line
           if MonthQE == 0
              currentData(1,[false(1,12),colQE]) = MonthQE;
           else
              currentData(1,[false(1,12),colQE]) = 1;  % if more then one QE announcement per month then only report one.
           end
        else
           %Meetings scheduled - keep information data collected above but report total change
           if ~isempty(currDatNoFO) % there was a change outsdie of FOMC
               outFOMCDate = datenum(currDatNoFO);
               firFOMCDate = datenum(currentData(1,1:3));
               if outFOMCDate < firFOMCDate % out of FOMC date occurred before scheduled meeting
                   %use information at beginning of prior month for
                   %prediction, set dummy in position 12 equal to 1 to
                   %signal this particular case
                   currentData = [currentData(1,1:2),zeros(1,2),currentData(1,3:6),currDatNoFO,1,data(i-1,:)];
                   currentData(1,3:4) = currentData(1,1:2); 
               else %if change at scheduled meeting occurred first, use info up to prior to meeting as collected in currentData
                   currentData = [currentData(1,1:2),zeros(1,2),currentData(1,3:6),currDatNoFO,0,currentData(1,7:end)];
                   currentData(1,3:4) = currentData(1,1:2); 
               end
           else %if there was no unscheduled change in Target, use info up to day before scheduled meeting as collected in currentData
               currentData = [currentData(1,1:2),zeros(1,2),currentData(1,3:6),zeros(1,4),currentData(1,7:end)];
               currentData(1,3:4) = currentData(1,1:2); 
           end
           % record total change during the month
           currentData(1,[false(1,12),colChange]) = MonthChange;
           if MonthQE == 0
              currentData(1,[false(1,12),colQE]) = MonthQE;
           else
              currentData(1,[false(1,12),colQE]) = 1;  % if more then one QE announcement per month then only report one.
           end
        end
        if outChangeFlag
            currentData(1,[false(1,12),outChange]) = 1;
        end
        if MeetingNum>0
            currentData(1,[false(1,12),colFOMC]) = 1;
        end
        %store data
         MonthData   = [MonthData;currentData];         
end
        