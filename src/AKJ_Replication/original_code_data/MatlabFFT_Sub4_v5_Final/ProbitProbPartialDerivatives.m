function pd = ProbitProbPartialDerivatives(y,X,par,Omega,score,J)

k    = size(X,2);
n    = length(y);
pd   = zeros(n,J);


for i = 1:n;
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
    g       = h*Omega*score;
    pd(i,:) = g';
end
