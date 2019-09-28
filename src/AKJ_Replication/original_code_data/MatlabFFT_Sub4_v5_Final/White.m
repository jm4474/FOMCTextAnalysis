function V = White(vt)

%implements automatic bandwidth selection of Newey&West 1994

T=size(vt,1);

mv = mean(vt);

V  = 1/T*((vt-ones(T,1)*mv)'*(vt-ones(T,1)*mv));

return
