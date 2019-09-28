function phat = ProbitPhat(par,y,X)

%computes estimated probabilities after Multinomial estimation

k  = size(X,2);
J  = length(par)/k+1;

par = reshape(par,k,J-1);

p   = zeros(length(y),J);

p(:,1) = cdf('norm',X*par,0,1); %standard normal cdf
p(:,J) = 1-p(:,1);
phat   = p;
return