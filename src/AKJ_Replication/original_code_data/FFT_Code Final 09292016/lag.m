function y=lag(x,i);

y=[zeros(i,size(x,2));x(1:end-i,:)];
return