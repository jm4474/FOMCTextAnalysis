function [A,resid,Covs,Jhh]=var_p(y,p,const)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%  Computes OLS estimates of VAR and residual covariance matrix        %
%  y=n*k matrix of observations                                        %
%  p=number of lags   
%  A estimated VAR parameters dimy times dimy*p matrix                 %
%  Residual Var-Cov matrix
%  Jhh Ng-Perron Wald test for significance of the p-th lag
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% X matrix of regressors
% A matrix of parameters

%build regressor matrix
r=size(y,2);
a=zeros(p*size(y,2),size(y,2));
n=size(y,1);
X=[zeros(1,r);y(1:n-1,:)];
for i=2:p
   X=[X [zeros(i,r);y(1:n-i,:)]];
end
y=y(p+1:n,:);
X=X(p+1:n,:);

if nargin==3 && const==1
   X=[ones(length(X),1), X];
end

% compute OLS estimator
Covs = X;
M=inv(X'*X);
A=M*(X'*y);
resid=y-X*A;
sigma=resid'*resid/n;
A1=reshape(A(r*(p-1)+1:r*p,:),r^2,1);
M1=M(r*(p-1)+1:r*p,r*(p-1)+1:r*p)*n;
Jhh=n*A1'*inv(kron(sigma,M1))*A1;
return


