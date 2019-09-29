function [vt,hdot,DET] = IRF_Residual(Phat,DP,y,X,ht,Theta,D,ky,hz,J,J0,T,Lscore,PCov,pnum,Tr,Ypick,TrendType)
% =========================================================================
% IRF_Residual
% ------------
% Computes residuals of IRF functions (denoted by v_t)
%
% date : 9/29/2016
% author : Sungho Noh
% =========================================================================

%% Create Weights
wgt = D./(Phat.^(2));
tau = repmat(wgt,[1,1,pnum]).*DP;
tau(isnan(tau)) = 0;                                                        % replace NaN with zeros
tau = repmat(tau(:,J0,:),[1,J,1]) - tau;                                    % weights in array of size = T_sub x J x number of pscore parameters

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

%% Compute Derivatives
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
    hdot = repmat(y_res,[1,1,J,pnum]).*permute(repmat(tau,[1,1,1,ky*hz]),[1,4,2,3]);
    hdot = reshape(squeeze(mean(hdot,1)),[ky*hz*J,pnum]);                   % take average and reshape into a matrix of size = (number of outcome x Horizon x J) x number of p-score parameters

else
    % if p-score estimates are bounded ====================================
    hdot = zeros(ky*hz*J,pnum);                                             % prepare storage
    for j = 1:J
        if j == J0
            hdot(ky*hz*(j-1)+1:ky*hz*j,:) = 0;                              % h_dot = 0 for baseline policy
        else
            y_j = y(~Tr(:,j),:);
            X_j = XX(~Tr(:,j),:);
            y_j_res = zeros(size(y));
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
            YY_j = repmat(y_j_res,[1,1,pnum]);                              % duplicate outcomes
            TAU_j = permute(repmat(squeeze(tau(:,j,:)),[1,1,ky*hz]),[1,3,2]);
            HD_j = sum(YY_j.*TAU_j,1)/T;                                    % take average, scaled by the total number of observations
            hdot(ky*hz*(j-1)+1:ky*hz*j,:) = squeeze(HD_j);                  % save into storage
        end
    end
end

%% Compute Residual Array
vt = ht - repmat(Theta',T,1) + Lscore*PCov*hdot';                           % compute residual array
vt(:,ky*hz*(J0-1)+1:ky*hz*J0) = [];                                         % drop columns associated with the baseline policy
DET = rcond(vt'*vt);                                                        % checking possible singularity in covariance

end