function stat = CompSpecTestStatm(mt,vt,WhiteFlag)
            T     = length(vt);
            if WhiteFlag                
                Omega = White(vt);
            else
                Omega = NeweyWest(vt);
            end
            if min(eig(Omega))<=0 && abs(min(eig(Omega)))>1.0e-10
                error('CompSpecTestm: Neg Definite Covariance Matrix');
            end            
            g     = mt'*ones(T,1)/sqrt(T);
            if max(abs(g))<1.0e-10 && max(eig(Omega))<1.0e-10
                stat = 0;      % set statistic to zero when Xtest variable is in the space spanned by the p-score covariates to avoid inaccuarate results
            elseif min(eig(Omega))<1.0e-10 %avoid computing the statistic for near singular covariance matrices
                stat = 0;
            else
                stat  = (g'/(Omega))*g;
            end
return