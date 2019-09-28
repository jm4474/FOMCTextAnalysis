function [MonthData,MonthColHead] = MergeTargetRate(MonthData,MonthColHead,TR,DateTR)

%function merges monthly data with Target Rate data by matching on monthly
%date

colY  = strcmp(MonthColHead,'Year');
colM  = strcmp(MonthColHead,'Month');

colTR = strcmp(MonthColHead,'Target Rate');


dM    = datenum(MonthData(:,colY),MonthData(:,colM),eomday(MonthData(:,colY),MonthData(:,colM)));

dTR   = datenum(DateTR(:,1),DateTR(:,2),eomday(DateTR(:,1),DateTR(:,2)));

[~,ia,ib] = intersect(dM,dTR);

% Save Target Rate Data in Monthly. This Target rate data is the level of
% the target rate in month (i) BEFORE a possible rate change occurs. Store
% this information in variable PSTargetRate for use as a possible covariate
% in the propensity score
PSTargetRate = MonthData(:,colTR);
MonthData      = [MonthData, PSTargetRate];
MonthColHead   = [MonthColHead, 'PSTargetRate'];

% copy target rate information with End of Month Target Rate. This data is
% used by GenSurprise.m to generate prediction variables. 
MonthData(ia,colTR) = TR(ib);
end
