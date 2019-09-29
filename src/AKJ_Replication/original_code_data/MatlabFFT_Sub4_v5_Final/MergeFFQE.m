function [Dailydata,Dailycolheaders] = MergeFFQE(Dailydata,Dailycolheaders,QEdata,QEcolh)

%This function merges the data file with daily FOMC target changes and the
%datafile with QE announcement dates

Dyear     = Dailydata(:,strcmp(Dailycolheaders,'Year'));
Dmonth    = Dailydata(:,strcmp(Dailycolheaders,'Month'));
Dday      = Dailydata(:,strcmp(Dailycolheaders,'Day'));

QEyear    = QEdata(:,strcmp(QEcolh,'Year'));
QEmonth   = QEdata(:,strcmp(QEcolh,'Month'));
QEday     = QEdata(:,strcmp(QEcolh,'Day'));

QE        = QEdata(:,strcmp(QEcolh,'qe'));

date      = datenum(Dyear,Dmonth,Dday);
QEdate    = datenum(QEyear,QEmonth,QEday);

qeid      = [];
e         = ones(size(date));
id        = [];

for i = 1:length(QEdate)
    [r,c]   = find(date == QEdate(i)*e);
    if ~isempty(r)
        qeid    = [qeid; i];
        id      = [id; r];
    end
end

Dailydata         = [Dailydata,zeros(length(Dyear),1)];
Dailydata(id,end) = QE(qeid,:);
Dailycolheaders   = [Dailycolheaders, 'qe'];

return