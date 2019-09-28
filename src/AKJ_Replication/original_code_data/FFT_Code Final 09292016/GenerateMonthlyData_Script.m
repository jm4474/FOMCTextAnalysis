clear;
% load xls data
fn = 'dataset_monthly_Nov6';
[num,txt,raw]=xlsread([fn '.xlsx']);

%convert missing values to zeros
t = isnan(num);
zs = zeros(size(num));
num(t) = zs(t);

if isempty(find(strcmp(txt,'Day'),1))
    %Add column with 'Day' and value 1
    txt = [txt(1:2),'Day',txt(3:end)]; 
    num  = [num(:,1:2), ones(length(num),1), num(:,3:end)];
end

% replace incompatible header names
stc = strcmp(txt,'Composite target R&R, Rudebusch, and FAME');
if ~isempty(find(stc,1))
    txt(stc) = {'Ctarget'};
end


stc = strcmp(txt,'R&R target changes');
if ~isempty(find(stc,1))
    txt(stc) = {'RRdtarget'};
end

stc = strcmp(txt,'R&R target');
if ~isempty(find(stc,1))
    txt(stc) = {'RRtarget'};
end

stc = strcmp(txt,'FAME target');
if ~isempty(find(stc,1))
    txt(stc) = {'Ftarget'};
end

stc = strcmp(txt,'Intermeeting moves');
if ~isempty(find(stc,1))
    txt(stc) = {'NonMeetChng'};
end

stc = strcmp(txt,'ED GSS method expectations');
if ~isempty(find(stc,1))
    txt(stc) = {'EDGSS'};
end

stc = strcmp(txt,'ED AJK method expectations');
if ~isempty(find(stc,1))
    txt(stc) = {'EDAJKexp'};
end

stc = strcmp(txt,'ED nonmeeting and intermtg move month expectations');
if ~isempty(find(stc,1))
    txt(stc) = {'EDAJKnonm'};
end


stc = strcmp(txt,'FFF AJK method expectations');
if ~isempty(find(stc,1))
    txt(stc) = {'FFFAJKexp'};
end

stc = strcmp(txt,'FFF nonmeeting and intermtg move month expectations');
if ~isempty(find(stc,1))
    txt(stc) = {'FFFAJKnonm'};
end

stc = strcmp(txt,'rrexpectations');
if ~isempty(find(stc,1))
    txt(stc) = {'RRexp'};
end

stc = strcmp(txt,'U rate');
if ~isempty(find(stc,1))
    txt(stc) = {'UNRATE'};
end

stc = strcmp(txt,'core pce');
if ~isempty(find(stc,1))
    txt(stc) = {'CPCE'};
end

stc = strcmp(txt,'Fed funds effective ');
if ~isempty(find(stc,1))
    txt(stc) = {'FFED'};
end

stc = strcmp(txt,'3 mo treasuries');
if ~isempty(find(stc,1))
    txt(stc) = {'RIFLGFCM03'};
end

stc = strcmp(txt,'1 yr treasury');
if ~isempty(find(stc,1))
    txt(stc) = {'RIFLGFCY01'};
end

stc = strcmp(txt,'2 yr treasuries ');
if ~isempty(find(stc,1))
    txt(stc) = {'RIFLGFCY02'};
end

stc = strcmp(txt,'10 yr treasuries');
if ~isempty(find(stc,1))
    txt(stc) = {'RIFLGFCY10'};
end

stc = strcmp(txt,'Most recent target change prior to this month');
if ~isempty(find(stc,1))
    txt(stc) = {'LastChange'};
end

stc = strcmp(txt,'Target rate on the day prior to meeting, or intermtg change if no mtg');
if ~isempty(find(stc,1))
    txt(stc) = {'r'};
end

stc = strcmp(txt,'Scale factor for when in month FOMC meeting occurs');
if ~isempty(find(stc,1))
    txt(stc) = {'Scale'};
end

s.data = num;
s.colheaders = txt;

save(['monthly_data.mat'],'s');
