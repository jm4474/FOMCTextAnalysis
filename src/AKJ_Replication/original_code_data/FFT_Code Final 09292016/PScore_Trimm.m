function [PhatTrimmed,ObsBounded,TrimInd] = PScore_Trimm(phat,min)
% -------------------------------------------------------------------------
% PScore_Trimm
% ------------
% replaces elements of which pscore estimates are less than min
%
% date : 9/28/2016
% modified by Sungho Noh
% -------------------------------------------------------------------------
TrimInd = (phat < min);
PhatTrimmed = phat.*(1-TrimInd) + min.*TrimInd;
ObsBounded = (sum(TrimInd,2) > 0);
fprintf('%3.0f / %3.0f estimate(s) is(are) replaced by trimming',[sum(sum(TrimInd)),size(phat,1)*size(phat,2)]);
end