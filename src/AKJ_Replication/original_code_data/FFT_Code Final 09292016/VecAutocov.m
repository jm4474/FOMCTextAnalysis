function V=VecAutocov(y,i)

n=size(y,1);
y_1=lag(y,i);
V=1/(n-1)*y'*y_1;
return