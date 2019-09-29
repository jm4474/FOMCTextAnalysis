function [hdot,dp] = Probithdot(yM,my,y,X,phat,par,J,zp)


%par is a matrix of parameters, each column contains the parameters for
%prob j, thus the matrix has dimension k x J-1
%X is the n x k matrix of covariates for the p-score
%y is the n x J matrix of dependent binary vars for the p-score. Each
%column is a binary variable indicating that the particular attribute j
%occured
%yM is the matrix of outcome variables of dimension n x #(impulse resp
%my is are the outcome vars yM projected onto the pscore covs X
%leads=IRL)

n       = size(y,1);
k       = size(X,2);
M       = size(yM,2);
par     = reshape(par,k,J-1);
hdot    = zeros(M*(J-1),k*(J-1));
selmhd  = eye(J-1);
selmhd  = [selmhd(:,1:zp-1),-ones(J-1,1),selmhd(:,zp:end)];
dp      = zeros(n,k*J*(J-1));

% selm is (J-1) x (J-1) selecting all but the j-th prob in row j - used to
% compute derivative w.r.t. to the param for the j-th prob
% selmhd is used to compute the difference between dj/pj-d0/p0.
% dp is a matrix with partial derivatives of the probabilities
% hdot is (IRL J) x Jk matrix with rows containing blocks of the hdot
% matrix for each of the five probabilities.

for i = 1:length(y);
    h = zeros(J,k*(J-1));  % allocate matrix for J-1 partial derivatives
    % for each observation store partial derivatives wrt to k(J-1)
    % parameters of all J probabilties where the prob are arranged by rows
    % and the derivatives are stored across the columns of h
    
    
    for j = 1:J % compute partial for each set of probabilities
        if j<J
           h(j,:) =  normpdf(X(i,:)*par,0,1)*X(i,:);
        else         %derivative wrt to the last prob = 1-P(x*b)
           h(j,:) =  -normpdf(X(i,:)*par,0,1)*X(i,:);
        end
    end
    g       = -(((y(i,:))./(phat(i,:).^2))'*ones(1,(J-1)*k)).*h;
    g1(1,:) = kron(g(1,:),yM(i,:)-squeeze(my(i,:,1)));
    g1(2,:) = kron(g(2,:),yM(i,:)-squeeze(my(i,:,2)));
    %hdot    = hdot + kron(selmhd*g,yM(i,:)'); 
    hdot    = hdot + reshape((selmhd*g1)',M,k); 
    dp(i,:) = reshape(h',k*J*(J-1),1)'; %store partial derivatives of probabilities w.r.t parameters
end

hdot = hdot/n;
return
