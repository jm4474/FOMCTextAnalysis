function y_Horizon = genLeads(y_subLong,T_sub,Horizon,option)
% -------------------------------------------------------------------------
% genLeads
% --------
% generate T_sub by L*ky array consists of leads of y variables upto L
% period / can choose between difference and level
%
% date : 10/16/2015
% modified by Sungho Noh
% -------------------------------------------------------------------------
[T_Long,ky] = size(y_subLong);
if strcmpi(option,'Diff')
    YY = y_subLong(2:T_Long,:) - y_subLong(1:T_Long-1,:);
elseif strcmpi(option,'Level')
    YY = y_subLong(2:T_Long,:);
else
    error('Unknown option for lead terms!');
end
y_Horizon = zeros(T_sub,ky*Horizon);
for ell = 1:Horizon
    t_use = (ell:T_sub+ell-1)';
    y_Horizon(:,ky*(ell-1)+1:ky*ell) = YY(t_use,:);
end

