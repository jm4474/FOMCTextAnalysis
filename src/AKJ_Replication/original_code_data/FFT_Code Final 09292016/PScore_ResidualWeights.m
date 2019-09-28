function Resid = PScore_ResidualWeights(phat,X,policy,menu,T,J,J0,Tr,Thres)
% -------------------------------------------------------------------------
% PScore_ResidualWeights
% ----------------------
% Calculates residual weights by fitting D/p where D is the policy
% indicator function and p is the predicted p-score onto X, the array of
% covariates. Result is T by J array of fitted residuals where T is the
% sample size and J is the number of choices.
%
% date : 12/11/2015
% modified by Sungho Noh
% -------------------------------------------------------------------------

policy_ind = (repmat(policy,1,J) == repmat(menu',T,1));
delta = policy_ind./phat;

% delta(delta > 1/Thres) = 1/Thres;

delta = delta - repmat(delta(:,J0),1,J);
delta(isnan(delta)) = 0;

if isempty(Tr) == 0
    Resid = zeros(size(delta));
    for j = 1:J
        if j < J0
            XX = X(~Tr(:,j),:);
            dd = delta(~Tr(:,j),j);
            bhat = (XX'*XX)\(XX'*dd);
            RR = dd - XX*bhat;
            Resid(~Tr(:,j),j) = RR;
        elseif j == J0
            Resid(:,j) = 0;
        else
            XX = X(~Tr(:,j-1),:);
            dd = delta(~Tr(:,j-1),j);
            bhat = (XX'*XX)\(XX'*dd);
            RR = dd - XX*bhat;
            Resid(~Tr(:,j-1),j) = RR;
        end 
    end
else
    XX = X;
    bhat = (XX'*XX)\(XX'*delta);
    Resid = delta-XX*bhat;
end

end