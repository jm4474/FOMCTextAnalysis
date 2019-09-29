function f = vec(A)

I = size(A,1);
J = size(A,2);

f = reshape(A,I*J,1);
return

