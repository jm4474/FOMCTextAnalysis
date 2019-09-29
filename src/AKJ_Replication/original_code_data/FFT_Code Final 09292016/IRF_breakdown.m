function [ht,IRF,IRF_out,IRFc_out] = IRF_breakdown(y,X,phat,D,T,J,J0,hz,ky,Tr,Ypick,TrendType)
% -------------------------------------------------------------------------
% IRF_breakdown
% -------------
% It first computes impulse-response estimates by taking weighted average
% of (residual) outcome variables. Weights are given by the inverse of
% propensity score estimates. In addition, long vector of estimates (stored
% as "IRF") is splitted into ky x 1 cell array where ky is the dimension of
% outcome variables.
%
% date : 9/29/2016
% author : Sungho Noh
% -------------------------------------------------------------------------

%% Create P-score Weights
wgt = D./phat;
wgt(isnan(wgt)) = 0;                                                        % trim NaN entries
wgt = wgt - repmat(wgt(:,J0),[1,J]);                                        % difference of inverse weights

%% Create Regressor Matrix
if isempty(Ypick) || isempty(TrendType)
    XX = X;                                                                 % without constant trend
elseif TrendType == 1
    XX = [ones(size(X,1),1),X];                                             % include vector of ones
elseif TrendType == 2
    XX = [(1:size(X,1))',X];                                                % include linear trend
else
    error('Unidentified TrendType');
end

%% Compute Weighted Average
if isempty(Tr)
    
    % if p-score estimates are not bounded ================================
    y_res = zeros(size(y));
    for k = 1:ky
        col_ind = zeros(1,ky);
        col_ind(k) = 1;
        col_ind = logical(repmat(col_ind,[1,hz]));                          % pick columns associated with kth outcome variable
        if sum((Ypick == k))
            % if variable k is subject to detrending
            Y_use = y(:,col_ind);
            Pi = (XX'*XX)\(XX'*Y_use);
            y_res(:,col_ind) = Y_use - XX*Pi;
        else
            % if variable k is NOT subject to detrending
            y_res(:,col_ind) = y(:,col_ind);
        end
    end
    ht = repmat(y_res,[1,J]).*kron(wgt,ones(1,hz*ky));                      % multiply residual outcomes with the weights
    IRF = mean(ht,1)';                                                      % take average

else
    
    % if p-score estimates are bounded ====================================
    ht = zeros(T,hz*ky*J);                                                  % storage for h_t's
    IRF = zeros(hz*ky*J,1);                                                 % storage for IRF estimates
    for j = 1:J
        if j == J0
            % response to baseline policy is set to be zero
            IRF((j-1)*hz*ky+1:j*hz*ky,1) = 0;
            
        else
            % response to every other policies
            y_j = y(~Tr(:,j),:);                                            % exclude truncated observations in outcome variable
            X_j = XX(~Tr(:,j),:);                                           % exclude truncated observations in regressors
            y_j_res = zeros(size(y));                                       % storage for residual outcomes
            for k = 1:ky
                col_ind = zeros(1,ky);
                col_ind(k) = 1;
                col_ind = logical(repmat(col_ind,[1,hz]));                  % pick columns associated with kth outcome variable
                if sum((Ypick==k))
                    % if variable k is subject to detrending
                    Y_use = y_j(:,col_ind);
                    Pi = (X_j'*X_j)\(X_j'*Y_use);
                    y_j_res(:,col_ind) = y(:,col_ind) - XX*Pi;
                else
                    % if variable k is NOT subject to detrending
                    y_j_res(:,col_ind) = y(:,col_ind);
                end
            end
            tau_j = wgt(~Tr(:,j),j)*ones(1,hz*ky);                          % duplicate weights
            ht_j = y_j_res(~Tr(:,j),:).*tau_j;                              % multiply residual outcomes with the weights
            ht(~Tr(:,j),(j-1)*hz*ky+1:j*hz*ky) = ht_j;                      % save h_t's
            IRF((j-1)*hz*ky+1:j*hz*ky,1) = mean(ht_j,1)';                   % take average
        end
    end
end

%% Break Estimates
IRF_in = reshape(IRF,hz*ky,J);                                              % reshape IRF: jth column corresponds to the response to jth policy
M = kron(tril(ones(hz,hz)),eye(ky));                                        % lower triangular part of matrix of ones
IRFc_in = M*IRF_in;                                                         % cumulative IRF
id = (1:hz*ky)';
IRF_out = cell(ky,1);                                                       % storage for IRFs
IRFc_out = cell(ky,1);                                                      % storage for cumulative IRFs
for k = 1:ky
    pick = zeros(ky,1);
    pick(k) = 1;                                                            % pick kth outcome varible among ky
    id_pick = id.*repmat(pick,[hz,1]);                                      % corresponding column numbers within long IRF vector
    id_pick(id_pick==0) = [];                                               % remove irrelevant entries
    IRF_out{k} = IRF_in(id_pick,:);                                         % save IRF
    IRFc_out{k} = IRFc_in(id_pick,:);                                       % save cumulative IRF
    IRF_out{k}(:,J0) = [];                                                  % remove column of baseline policy
    IRFc_out{k}(:,J0) = [];                                                 % remove column of baseline policy
end

end