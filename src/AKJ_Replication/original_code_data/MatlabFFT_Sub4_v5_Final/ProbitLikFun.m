function [lik,grad] = ProbitLikFun(par,y,X)

%assumes that the first column of data is dependent var

%y  = data.y;
%X  = data.X;

k  = size(X,2);
J  = length(par)/k+1;

if J>2
    error('ProbLikFun: not supported for multinomial case');
end

par = reshape(par,k,J-1);

p   = zeros(length(y),J);
p(:,1) = cdf('norm',X*par(:,1),0,1); %standard normal cdf

p(:,J)     = 1-p(:,1);
l          = log(p);

lik = 0;
for i = 1:J
    lik = lik + y(:,i)'* l(:,i);
end

n     = length(y);
grad = ProbitLikFunGrad(par,y,X);
grad = (ones(1,n)*grad)';


lik = - lik; %minimize negative of lik
grad = - grad;
return

    
    