function [PhatTrunc,DateLoc,TruncInd] = PScore_Truncate(phat,policy,min,menu,J,J0)
% =========================================================================
% PScore_Truncate
% ---------------
% Pick locations where estimated p-scores are less than the pre-fixed
% threshold.
%
% date : 9/29/2016
% modified by Sungho Noh
% =========================================================================

policy_ind = (repmat(policy,1,J) == repmat(menu',length(policy),1));

PhatBound = 1*(1-policy_ind) + phat.*policy_ind;                            % if D=j, leave phat(j) and set all the other terms to be arbitarly large (equal to one)
ind = (PhatBound <= min);                                                   % =1 if D=j and phat(j) < min
DateLoc = (sum(ind,2) > 0);                                                 % observations to be truncated
PhatTrunc = max(phat,min);

ind0 = repmat(ind(:,J0),1,J);
TruncInd = (ind + ind0 > 0);                                                % =1 either if phat(j) < min or phat(J0) < min, size : T_sub x (J-1)
TruncInd(:,J0) = 0;

fprintf('%3.0f / %3.0f observation(s) is(are) truncated',sum(DateLoc),length(DateLoc));
end
