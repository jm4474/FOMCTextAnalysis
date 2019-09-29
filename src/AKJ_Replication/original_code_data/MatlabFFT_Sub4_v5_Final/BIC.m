function bic   = BIC(T,G,IW,IWW,vecH,numpar,numres)

k   = numpar - numres;
SSR = (IW'*vecH - IWW*G)'*(IW'*vecH - IWW*G);
bic = log(SSR/T)+log(T)*k/T;
return
