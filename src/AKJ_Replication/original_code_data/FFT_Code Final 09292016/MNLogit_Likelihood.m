function [Lik,Grad,Hess,Prob,DProb] = MNLogit_Likelihood(Psi,Y,Z,J,Y_choice,output_option)
% -------------------------------------------------------------------------
% Evaluation of Log-Likelihood of Multinomial Logit Model
%
% author : Sungho Noh
% date   : 10/4/2015
%
% INPUT(S)
% --------
% Psi : Jk by 1 vector of parameter values where the likelihood is evaluated
% Y : vector of discrete outcomes among 0,1,...,J
% Z : matrix of covariates, contains k columns (with constant)
% J : number of choices (other than base outcome)
% Y_choice : set of possible discrete outcomes, baseline enters into the
% first element of the vector
% output_option : if empty, function serves as the objective of fminunc
%
% OUTPUT(S) : when output_option is empty
% ---------------------------------------
% Lik : negative of log-likelihood
% Grad : Jk by 1 gradient
%
% OUTPUT(S) : when output_option is not empty
% -------------------------------------------
% Lik : vector of marginal likelihoods
% Grad : T by Jk array, 1 by Jk gradient vectors stacked by t
% Hess : Jk by Jk Hessian matrix
% Prob : T by J+1 predicted probability
% DProb : T by Jk by J+1 derivative of Prob w.r.t. parameters
%
% NOTES
% -----
% as a normalization, coefficients corresponding to the base outcome are
% set to be zero
% -------------------------------------------------------------------------

T = length(Y);                                                             % sample size
k = size(Z,2);                                                             % number of covariates
Psi_use = reshape(Psi,[k,J]);                                              % re-arrange input parameter into matrix form
YY = repmat(Y,1,J+1);
choice = repmat(Y_choice',T,1);                                            % menu of choices
D = (YY == choice);                                                        % find location of the chosen outcome in the menu
Pmat = [ones(T,1), exp(Z*Psi_use)];
PP = Pmat./repmat(sum(Pmat,2),1,J+1);                                      % probabilities / pscore on each choice

ell = sum(D.*log(PP),2);                                                   % log likelihood for each observation

DP = kron(D-PP,ones(1,k));
Z_rep = repmat(Z,1,J+1);
G = DP.*Z_rep;
G = G(:,k+1:k*(J+1));                                                      % gradient vectors

if isempty(output_option) == 1                                             % produce likelihood and gradient only
    if nargout > 1
        Lik = -sum(ell);
        Grad = -sum(G)';
    else
        Lik = -sum(ell);
    end

else                                                                       % compute further results
    Lik = ell;
    Grad = G;
    Prob = PP;                                                             % predicted probability
    H = zeros(T,k*(J+1),k*(J+1));                                          % storage for Hessian matrix
    DProb = zeros(T,k*J,J+1);                                              % storage for derivative with respect to the coefficients
    for t = 1:T
        DPt = diag(PP(t,:)) - PP(t,:)'*PP(t,:);
        H(t,:,:) = -kron(DPt,Z(t,:)'*Z(t,:));
        DProb(t,:,:) = kron(DPt(2:J+1,:),Z(t,:)');
    end
    Hess = squeeze(sum(H(:,k+1:k*(J+1),k+1:k*(J+1)),1));
    
end