function [ac,acs] = autocorr(y,l)

n   = size(y,1);
k   = size(y,2);
ac  = zeros(l,k);
acs = zeros(l,k);

for i = 1:l
    cm       = diag(corr(y,lag(y,i)))';
    ac(i,:)  = cm(1,:);
    acs(i,:) = sqrt(n)*ac(i,:);
end
return
    