function stat = CompSpecTestStat(vt,WhiteFlag)
            T     = length(vt);
            if WhiteFlag
                Omega = White(vt);
            else
                Omega = NeweyWest(vt);
            end
            g     = vt'*ones(T,1)/sqrt(T);
            stat  = (g'/(Omega))*g;
return