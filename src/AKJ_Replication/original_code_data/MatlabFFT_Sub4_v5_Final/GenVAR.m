function y = GenVAR(Ac,UStar,T,p,d)

Y1    = zeros(d*p,1);
A     = [Ac(2:end,:)';[eye(d*(p-1)),zeros(d*(p-1),d)]];
E     = [eye(d);zeros(d*(p-1),d)];
y     = zeros(T,d);

for i = 1:T
    Y1= E*Ac(1,:)'+A*Y1+E*UStar(i,:)';
    y(i,:) = E'*Y1;
end
return
