function aic   = AIC(T,G,IW,IWW,vecH,numpar,numres)

k   = numpar - numres;
SSR = (IW'*vecH - IWW*G)'*(IW'*vecH - IWW*G);
aic = log(SSR/T)+2*k/T;
return
