function [Dailydata,Dailycolheaders] = MergeFRBH15(Dailydata,Dailycolheaders,H15data,H15colh)

%This function merges the data file with daily FOMC target changes and the
%datafile with H15 announcement dates

Dyear     = Dailydata(:,strcmp(Dailycolheaders,'Year'));
Dmonth    = Dailydata(:,strcmp(Dailycolheaders,'Month'));
Dday      = Dailydata(:,strcmp(Dailycolheaders,'Day'));

H15year    = H15data(:,strcmp(H15colh,'Year'));
H15month   = H15data(:,strcmp(H15colh,'Month'));
H15day     = H15data(:,strcmp(H15colh,'Day'));
dataInd    = ~(strcmp(H15colh,'Year') | strcmp(H15colh,'Month') | strcmp(H15colh,'Day'));
H15        = H15data(:,dataInd);

date      = datenum(Dyear,Dmonth,Dday);
H15date    = datenum(H15year,H15month,H15day);

H15id      = [];
e         = ones(size(date));
id        = [];

for i = 1:length(H15date)
    [r,c]   = find(date == H15date(i)*e);
    if ~isempty(r)
        H15id    = [H15id; i];
        id      = [id; r];
    end
end
DDc                     = size(Dailydata,2);
H15c                    = size(H15,2);
Dailydata               = [Dailydata,zeros(length(Dyear),H15c)];
Dailydata(id,DDc+1:end) = H15(H15id,:);
Dailycolheaders         = [Dailycolheaders, H15colh(dataInd)];

return