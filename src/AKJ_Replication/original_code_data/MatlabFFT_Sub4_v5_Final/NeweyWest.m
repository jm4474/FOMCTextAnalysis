function V=NeweyWest(vt)

%implements automatic bandwidth selection of Newey&West 1994

T=size(vt,1);
d=size(vt,2);
n=floor(4*(T/100)^(2/9));
c_gamma=1.1447;

vt_1=[zeros(1,d);vt(1:end-1,:)];
A_hat=zeros(d,d);

for i=1:d;
    A_hat(i,i)=(vt_1(:,i)'*vt_1(:,i))\(vt_1(:,i)'*vt(:,i));
end
v_hat=vt-vt_1*A_hat;
Omega0=1/(T-1)*(v_hat'*v_hat);
s_hat0=ones(1,d)*Omega0*ones(d,1);
s_hat1=0;
for i=1:n;
    s(i).Omega=VecAutocov(v_hat,i);
    s_hat0=s_hat0+2*ones(1,d)*s(i).Omega*ones(d,1);
    s_hat1=s_hat1+2*i*ones(1,d)*(s(i).Omega)*ones(d,1);
end
s_hat0 = abs(s_hat0);
s_hat1 = abs(s_hat1);
gamma=c_gamma*(s_hat1/s_hat0)^(2/3);
B_hat=min(floor(gamma*T^(1/3)),n);
V=Omega0;
for i=1:B_hat
    V=V+(1-i/(B_hat+1))*((s(i).Omega)+(s(i).Omega)');
end

Ainv=inv(eye(d)-A_hat);
V=Ainv*V*Ainv;
return
