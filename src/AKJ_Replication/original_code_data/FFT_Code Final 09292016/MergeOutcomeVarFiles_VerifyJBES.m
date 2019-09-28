function [s,y,dy,ind,dyMonth] = MergeOutcomeVarFiles_VerifyJBES(respvfn,respvfn1,Start,End)

% Load outcome variable datafile and prepare input data 
s            = load(respvfn);
s            = s.s;
y            = fillforward(s.data);          % Outcome data
year         = s.data(:,strcmp(s.colheaders,'Year'));
month        = s.data(:,strcmp(s.colheaders,'Month'));
%day          = s.data(:,strcmp(s.colheaders,'Day'));
%if isempty(day)
    day      = eomday(year,month);   
%end

dy           = datenum(year,month,day);
y            = y((dy>=Start & dy<=End),:);  %select data within Sample range
dy           = dy(((dy>=Start & dy<=End))); %select dates within Sample range

[ind,dyMonth]= lastDayOfMonth(dy);

if ~isempty(respvfn1)
    s1            = load(respvfn1);
    s1            = s1.s;
    y1            = fillforward(s1.data);          % Outcome data
    ycol          = strcmp(s1.colheaders,'Year');
    mcol          = strcmp(s1.colheaders,'Month');
    dcol          = strcmp(s1.colheaders,'Day');
    year1         = s1.data(:,ycol);
    month1        = s1.data(:,mcol);
    day1          = s1.data(:,dcol);
    %if isempty(day1) Correction to read monthly data where day1=1
        day1         = eomday(year1,month1);
     
    %end

    dy1           = datenum(year1,month1,day1);
    y1            = y1((dy1>=Start & dy1<=End),~logical(mcol+ycol+dcol));  %select data within Sample range
    dy1           = dy1(((dy1>=Start & dy1<=End))); %select dates within Sample range    
    
    [~,ia,ib]    = intersect(dyMonth,dy1);
    k            = size(y,2);
    y            = [y,zeros(size(y,1),size(y1,2))];
    y(ind(ia),k+1:end)= y1(ib,:);
    y            = fillforward(y);
    s.colheaders = [s.colheaders,s1.colheaders(~logical(mcol+ycol+dcol))];
end