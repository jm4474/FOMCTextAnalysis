function grad = ProbitLikFunGrad(par,y,X)

%computes the gradient for each observation


J  = size(par,2)+1;
if J>2
    error('ProbLikFunGrad not supported for multinomial probit')
end


grad = zeros(length(y),size(X,2)*(J-1));
for i = 1:length(y);
    d = cdf('norm',X(i,:)*par,0,1);
    e = (1-d)*d;
    f = normpdf(X(i,:)*par,0,1);
    h = zeros(size(X,2),J-1);  % allocate matrix for J-1 partial derivatives
    h(:,1) = ((y(i,1)-d)/e)*f*X(i,:)';
    g    = reshape(h,size(X,2)*(J-1),1); % vectorize the gradient
    grad(i,:) = g';
end

return

    
    