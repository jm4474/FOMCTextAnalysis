function Omega = IRFCov_White(v,T_sub)
% =========================================================================
% IRFCov_White
% ------------
% Computes covariance matrix of IRF and cumulative IRF via White (1980)
%
% date : 11/26/2015
% author : Sungho Noh
% =========================================================================

Omega = (v'*v)/T_sub;

end