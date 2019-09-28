function [X,ProScorVarN,Dummy] = AddDummy(X,ProScorVarN,dyMonth,ib,DumName,Start,End)

%adds a Dummy Variable to the p-score covariates
%DumName: String dummy variable name
%Start: String Start Date, set to [] if no start date
%End  : String End Date, set to [] if no end date

if ~isempty(Start)
    dDummys  = datenum(Start);
else
    % if no start use first obs
    dDummys  = dyMonth(1,:);
end
if ~isempty(End);
    dDummye  = datenum(End);
else
    %if no end use last obs
    dDummye  = dyMonth(end,:);
end
iDummy        = logical((dyMonth(ib)>=dDummys).*(dyMonth(ib)<=dDummye));
Dummy         = zeros(length(ib),1);
numDummy      = ones(length(ib),1)'*iDummy;
Dummy(iDummy) = ones(numDummy,1);
X             = [X,Dummy];
ProScorVarN   = [ProScorVarN;DumName];
end