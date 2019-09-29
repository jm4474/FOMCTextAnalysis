function [COV,COVc,COVj,COVcj,COVjhz,COVcjhz] = IRFCov_breakdown(Omega,ky,hz,J)
% =========================================================================
% IRFCov_breakdown
% ----------------
% takes the full-sized covariance matrix (dimension = ky x Horizon x J-1)
% and breaks down into a number of cell arrays
%
% date : 11/26/2015
% author : Sungho Noh
% =========================================================================

L = ky*hz*(J-1);                                                           % L = ky x Horizon x J-1 (excluding baseline outcome)
id = (1:L)';                                                               % index of columns for later use

% Prepare storages
COV = cell(ky,1);
COVc = cell(ky,1);
COVj = cell(ky,hz);
COVcj = cell(ky,hz);
COVjhz = cell(ky,1);
COVcjhz = cell(ky,1);
MM = kron(eye(J-1),tril(ones(hz,hz)));                                     % lower triangular matrix of ones to cumulate variances

% Split full covariance matrix
for k = 1:ky
    pick = zeros(ky,1);
    pick(k) = 1;                                                           % pick kth varible among ky
    num_pick = id.*repmat(pick,hz*(J-1),1);
    num_pick(num_pick==0) = [];                                            % eliminate unwanted rows
    Omega_pick = Omega(num_pick,num_pick);                                 % pick relevant elements in the full covariance matrix and scale down by the sample size
    Omega_cumm = MM*Omega_pick*MM';                                        % compute cumulative covariances
    COV{k} = reshape(sqrt(diag(Omega_pick)),hz,(J-1));                     % store diagonal elements in covariance of IRF
    COVc{k} = reshape(sqrt(diag(Omega_cumm)),hz,(J-1));                    % store diagonal elements in covariance of cumulative IRF
    COVjhz{k} = Omega_pick;                                                % store off-diagonal elements in covariance of IRF
    COVcjhz{k} = Omega_cumm;                                               % store off-diagonal elements in covariance of sumulative iRF
    for h = 1:hz
        pick_h = zeros(hz,1);
        pick_h(h) = 1;
        id_pick = (1:hz*(J-1))'.*(repmat(pick_h,J-1,1));
        id_pick(id_pick==0) = [];
        COVj{k,h} = Omega_pick(id_pick,id_pick);                           % store covariance of IRF for each y and each horizon
        COVcj{k,h} = Omega_cumm(id_pick,id_pick);                          % store covariance of cumulative IRF for each y and each horizon
    end
end

end