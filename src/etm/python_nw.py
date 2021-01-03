
import pandas as pd
import numpy as np

import numpy as np
class resultobject:
    method = 'nwest'

def newey(y,x,nlag):
    nobs, nvar = np.shape(x)
    #print(nobs)
    try:
        x =x.to_numpy()
        y =y.to_numpy()
    except:
        pass            
    results = resultobject()
    
   
    setattr(results,"y",y)
    setattr(results,"nobs",nobs)
    setattr(results,"nvar",nvar)
    
    xpxi = np.linalg.inv(x.transpose()@ x)
    setattr(results,"beta", xpxi @ x.transpose() @ y)
    
    setattr(results,"yhat", x @ results.beta)

    setattr(results,"resid", y - results.yhat)
    sigu = results.resid.transpose() @ results.resid 
    setattr(results,"sige", sigu / (nobs-nvar))
    
    emat = np.tile(results.resid.transpose(),(nvar,1))
    hhat = np.multiply(emat, x.transpose())
    
    G = np.zeros((nvar,nvar))
    w = np.zeros((2*nlag+1,1)) 
    a = 0 
     
    while a<nlag+1:
        ga = np.zeros((nvar,nvar)) 
        w[nlag+a,0] = (nlag+1-a)/(nlag+1) 
        za=hhat[:,a:nobs] @ hhat[:,0:nobs-a].transpose()
        if a==0:
            ga=ga+za 
        else: 
            ga=ga+za+za.transpose() 
        G=G+w[nlag+a,0] * ga; 
        a+=1
    
     
    V=xpxi @ G @ xpxi; 
    nwerr= np.sqrt(np.diag(V))
     
    setattr(results,"tstat", results.beta / nwerr)
    ym = y - np.mean(y)
    rsqr1 = sigu
    rsqr2 = np.dot(ym, ym)
    setattr(results,"rsqr", 1.0 - rsqr1/rsqr2)
    rsqr1 = rsqr1/(nobs-nvar)
    rsqr2 = rsqr2/(nobs-1.0)
    setattr(results,"rbar",1 - (rsqr1/rsqr2))
    ediff = results.resid[1:nobs] - results.resid[0:nobs-1] 
    setattr(results,"dw", (ediff @ ediff) / sigu)

    return results












