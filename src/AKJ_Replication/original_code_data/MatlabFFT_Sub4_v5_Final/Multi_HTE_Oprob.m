function [Gamma,V_Gamma,V,fit,fit1,GammaPar,GammaParCum,D,phat,dp0,dps,TestData,score,VarLogit,ht,h_dot1,DeletedObs]...
     =Multi_HTE_Oprob(y,X,actual,phat,score,VarLogit,xb,cut,zp,cutlev,HTSamp,MulHTEpar)
                                  
%postiion of the element in phat where zero element sits:zp
%D is matrix of dummies coded after the dependent variable categories in
%cutlev
%phat is the estimated probabiltiies by categories
%dp0 are the derivatives of estimated probability at baseline (indexed by
%zp) with respect to all parameters (betas and estimators for the cut
%levels in cut)
%dps contains the derivatives of the remaining probabilties with respect
%to all parameters. These inputs are needed for the specification tests in a separate module
%kappa is the fraction of HT estimation sample size relative to p-score
%estimation sample size


Z = GenDeltaControls(X,MulHTEpar);   % select detrending controls for delta
D = Actual2D(actual,cutlev);
n      = size(y,1);
d      = size(y,2);
numlev = size(cutlev,1);
k      = size(X,2)+numlev-1; %number of parameters

ht     = zeros(n,d*(numlev-1));
htv    = zeros(n,d*(numlev-1));
cc     = 0;


if MulHTEpar.Truncate && MulHTEpar.Trimm
    error('Multi_HTE_Oprob: Cannot truncate and trim at the same time');
elseif MulHTEpar.Truncate
    lowp    = (phat<=MulHTEpar.TruncThs);
    phat    = max(phat,MulHTEpar.TruncThs);
elseif MulHTEpar.Trimm
    lowp    = (phat<=0);
    phat    = max(phat,MulHTEpar.TrimmThs);
else
    lowp    = (phat<=0.000001);
    phat    = max(phat,0.000001); % use minimal trimming to avoid NaN
end



lowp       = logical(D.*lowp); %identify observations where D=1 and p<threshold
goodp      = ~lowp;
fit        = D.*phat;
fit1       = (ones(n,size(D,2))-D).*phat;
DeletedObs = datestr(HTSamp((sum(lowp,2)>0),:));


%compute delta_0
dpX    = ((normpdf(cut(zp-1,1)*ones(n,1)-xb,0,1)-normpdf(cut(zp,1)*ones(n,1)-xb,0,1))*ones(1,size(X,2))).*X;
dp     = [dpX, zeros(n,zp-2), -normpdf(cut(zp-1,1)*ones(n,1)-xb,0,1),normpdf(cut(zp,1)*ones(n,1)-xb,0,1),zeros(n,numlev-zp-1)]; % Derivative wrt cut
h_dot0 = (((-D(:,zp)./((phat(:,zp)).^2))*ones(1,k)).*dp);
dp0    = dp;
dps    = [];
h_dot1=[];

%compute delta_j
for i=1:numlev;
    if i~=zp
       cc=cc+1; 
       if i==1
          dpX = (-normpdf(cut(i,1)*ones(n,1)-xb,0,1)*ones(1,size(X,2))).*X;
          dp  = [dpX, normpdf(cut(i,1)*ones(n,1)-xb,0,1), zeros(n,numlev-2)]; % Derivative wrt cut1
       elseif i==numlev
          dpX = (normpdf(cut(i-1,1)*ones(n,1)-xb,0,1)*ones(1,size(X,2))).*X; 
          dp  = [dpX, zeros(n,numlev-2),-normpdf(cut(i-1,1)*ones(n,1)-xb,0,1)]; % Derivative wrt cut2
       else
          dpX = ((normpdf(cut(i-1,1)*ones(n,1)-xb,0,1)-normpdf(cut(i,1)*ones(n,1)-xb,0,1))*ones(1,size(X,2))).*X;
          dp  = [dpX, zeros(n,i-2), -normpdf(cut(i-1,1)*ones(n,1)-xb,0,1),normpdf(cut(i,1)*ones(n,1)-xb,0,1),zeros(n,numlev-1-i)]; % Derivative wrt cut
       end
       
       goodp(:,i) = goodp(:,i).*goodp(:,zp);
       delta  = D(:,i)./phat(:,i)-D(:,zp)./phat(:,zp);
       h_dotj = (((-D(:,i)./((phat(:,i)).^2)*ones(1,k)).*dp));         
       dps    = [dps, dp];                
       if MulHTEpar.DemeanDelta
           Zg      = Z(goodp(:,i),:);
           deltam  = Z/(Zg'*Zg)*Zg'*delta(goodp(:,i),:);
           ht(:,(cc-1)*d+1:cc*d)     = (y.*((delta-deltam)*ones(1,d)));
           my                        = Z/(Zg'*Zg)*Zg'*y(goodp(:,i),:);
           htv(:,(cc-1)*d+1:cc*d)    = ((y-my).*(delta*ones(1,d)));
           h_dot1 = [h_dot1;1/n*(y-my)'*(h_dotj-h_dot0)]; %Standalone code does not subtract my                      
%           h_dot1 = [h_dot1;1/n*y'*(h_dotj-h_dot0)];
       else
           htv(:,(cc-1)*d+1:cc*d)    = (y.*(delta*ones(1,d)));
           ht(:,(cc-1)*d+1:cc*d)     = (y.*(delta*ones(1,d)));
           h_dot1 = [h_dot1;1/n*y'*(h_dotj-h_dot0)];
           deltam = zeros(size(delta));
       end
       if i==2
           goodp_N25 = goodp(:,i);
           delta_N25 = delta;
           deltaDD_N25 = delta-deltam;
           h_dotN25 = h_dotj;
       elseif i==4
           goodp_P25 = goodp(:,i);
           delta_P25 = delta;
           deltaDD_P25 = delta-deltam;
           h_dotP25 = h_dotj;           
       end

    end
end

vt = htv + score*VarLogit*h_dot1';  

dimv        = size(vt,2);
indmat      = reshape(1:dimv,d,numlev-1);
Gamma       = zeros(1,dimv);
GammaPar    = zeros(size(indmat));
GammaParCum = zeros(size(indmat));
for i=1:numlev-1
    lgp                  = sum(goodp(:,i));
    if i < zp
       Gamma(:,indmat(:,i)) = mean(htv(goodp(:,i),indmat(:,i)));
       vt(goodp(:,i),indmat(:,i)) = vt(goodp(:,i),indmat(:,i)) -ones(lgp,1)* Gamma(:,indmat(:,i));
    else
       Gamma(:,indmat(:,i)) = mean(htv(goodp(:,i+1),indmat(:,i)));
       vt(goodp(:,i),indmat(:,i)) = vt(goodp(:,i),indmat(:,i)) - ones(lgp,1) * Gamma(:,indmat(:,i));
    end
    if strcmp(MulHTEpar.CovMethod,'NW')
        V(i).Gamma           = NeweyWest(vt(goodp(:,i),indmat(:,i))-ones(lgp,1)*mean(vt(goodp(:,i),indmat(:,i))))';
    elseif strcmp(MulHTEpar.CovMethod,'White')
        V(i).Gamma           = White(vt(goodp(:,i),indmat(:,i))-ones(lgp,1)*mean(vt(goodp(:,i),indmat(:,i))))';
    else
        error('Multi_HTE_Oprob: Covariance Matrix Method not supported - chose MulHTEpar.CovMethod={NW,White}');
    end
end


if strcmp(MulHTEpar.CovMethod,'NW')
    V_Gamma = NeweyWest(vt);
elseif strcmp(MulHTEpar.CovMethod,'White')
    V_Gamma = White(vt);    
else
    error('Multi_HTE_Oprob: Standard Error method not supported - use NW or White');
end

TestData.delta_N25 = delta_N25;
TestData.delta_P25 = delta_P25;
TestData.deltaDD_N25 = deltaDD_N25;
TestData.deltaDD_P25 = deltaDD_P25;
TestData.goodp_N25 = goodp_N25;
TestData.goodp_P25 = goodp_P25;
TestData.h_dotN25  = h_dotN25;
TestData.h_dotP25  = h_dotP25;
TestData.Z         = Z;

return