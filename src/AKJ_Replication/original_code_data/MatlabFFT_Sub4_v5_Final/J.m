function  [Jstat,Jpval,critval] = J(GammaNC,Gamma,V_Gamma,dg,N)

Jstat   = N*(GammaNC-Gamma)*inv(V_Gamma)*(GammaNC-Gamma)';

Jpval   = 1-cdf('chi2',Jstat,dg);

critval = icdf('chi2',.95,dg);
return

