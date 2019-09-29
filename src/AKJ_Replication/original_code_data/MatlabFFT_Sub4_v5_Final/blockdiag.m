function A = blockdiag(B)

J = size(B,2);
n = size(B,1);
A = zeros(n*J,J);
for j = 1:J
    ej      = zeros(J,1);
    ej(j,1) = 1;
    A       = A + kron(ej*ej',B(:,j));
end
return