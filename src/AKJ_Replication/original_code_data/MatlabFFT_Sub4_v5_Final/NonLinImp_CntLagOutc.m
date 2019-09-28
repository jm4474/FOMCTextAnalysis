function Model = NonLinImp_CntLagOutc(Model)

% Unpack Structure variables for easier access
pval          = [];
LR            = [];
pvLR          = [];

level        = Model.level;
numlev       = Model.numlev;

y            = Model.y;
[DD,DVarN]   = Actual2D(y,level);

yQE          = [];
yQEps        = [];
if Model.MultiNomQE && ~Model.MultiNomQEonly;
   yQE       = Model.yQE;
elseif Model.MultiNomQE && Model.MultiNomQEonly
   y         = Model.yQE;
   level     = [0;1];
   numlev    = 2;
   yQE       = [];   
end

Model.yMDS   = Model.yM; %Save outcome variable for descriptive Stats
yM           = Model.yM;
X            = Model.X;
Xtest        = Model.Xtest;
Ytest        = Model.Ytest;
zp           = Model.zp;
hor          = Model.ImpHorizon;

%Select Estimation Sample

[~,ia,~]     = intersect(Model.SampDat,Model.PsSampDat);

EstSampDates = Model.PsSampDat(ia,:);

Xps          = X(ia,:);
yps          = y(ia,:);
if ~isempty(yQE)
    yQEps    = yQE(ia,:);
end


switch Model.PScore
     case 'Oprob'

        % Generate input data for the Order Probit estimation of the policy model

        oprob_in.DATA = [yps,Xps];
        oprob_results = MATLAB_Ordered_Probit_Estimate(oprob_in);
        nlik          = length(yps);
        n             = nlik;
        par           = oprob_results.Beta;        
        xb            = X*par;
        score         = oprob_results.First_Derivative;
        phat          = oprob_results.phat;
        phatps        = phat;
        cut           = oprob_results.Cut_Points;
        Lik           = oprob_results.Likelihood.LLV;
        numpar        = size(par,1)+size(cut,1);
        actual        = y;
        Omega         = inv(-oprob_results.Hessian/n);
        VarLogit      = Omega;
        stde          = sqrt(diag(Omega))/sqrt(n);
        tstat         = [par;cut]./stde;
        pval          = 2*(1-tcdf(abs(tstat),n-1));
        if numlev == 5
           XVarN         = [Model.ProScorVarN;'cut1';'cut2';'cut3';'cut4'];
        else
           XVarN         = [Model.ProScorVarN;'cut1';'cut2'];
        end
       
    case 'Probit'
        
                % Generate input data for the Order Probit estimation of the policy model
        disp('Estimating Probit Model');
        tic
        probit_results = probitEst(yps,Xps,yQEps,level,numlev,Model.ProScorVarN);
        toc
        nlik          = length(yps);
        n             = nlik;
        par           = probit_results.Beta;
        effnumlev     = probit_results.effnumlev;
        levInd        = probit_results.levInd;
        pInd          = [];%probit_results.pInd;
        par           = reshape(par,size(par,1)/max((effnumlev-1),1),max(effnumlev-1,1));
        xb            = X*par;
        numpar        = length(probit_results.Beta);
        score         = [];
        phat          = probit_results.phat;
        phatps        = phat;
        actual        = probit_results.y;
        Omega         = inv(probit_results.hessian/n);  %because the negative of the lik is minimized, no neg sign needed here
        VarLogit      = Omega;
        fit           = probit_results.fit;       
        fit1          = probit_results.fit1;
        numlev        = effnumlev;
        stde          = sqrt(diag(Omega))/sqrt(n);
        Lik           = probit_results.fval;
        tstat         = probit_results.t;
        pval          = probit_results.pval;
        LR            = probit_results.LR;
        pvLR          = probit_results.pvLR;
        PR2           = probit_results.PR2;
        XVarN         = probit_results.VarN;
        cut           = [];
        
      
          
end
% Prepare input for Multi_HTE - Nonlinear Impulse Response Routine

%if strcmp(Model.DemeanMethod,'HPBK') || strcmp(Model.DemeanMethod,'BPBK')
if Model.MulHTEpar.DemeanDelta 
   wnd        =  Model.MulHTEpar.DemeanDeltaW;
else
   wnd        = 0;
end


[~,ic,icc]   = intersect(Model.PsSampDat,Model.HTSampDat(1+wnd:end-hor,:));
[~,id,~]   = intersect(Model.SampDat,Model.HTSampDat);
[~,ie,~]   = intersect(ia,ic);
[~,ig,~]   = intersect(Model.SampDat,Model.PsSampDat);


HTSampDates = Model.HTSampDat(icc,:);

phat    = phat(ie,:);
if ~isempty(score)
    score   = score(ie,:);
end
yMFit   = yM(ig,:);  % Store data for Fit graphs
actual  = actual(ie,:);
xb      = xb(ie,:);
X       = X(ie,:);
Xtest   = Xtest(ie,:);
yM      = yM(id,:);
Ytest   = Ytest(id,:);
yMj     = zeros(size(X,1),size(yM,2));
yMspecT = zeros(size(X,1),size(yM,2));

Ytest   = Ytest(1+wnd:end-hor,:);

res     = struct('g',[],'gs',[],'gc',[],'gcs',[]);
 
for i = 1:size(yM,2);         % for each column of yM constract hor-leads
    outVarN   = Model.OutcomeVarN(i,1);
    MulHTEpar = Model.MulHTEpar;
    outVar    = zeros(size(yM,1),hor);
    outVarZ   = [];
    for j  = -wnd:hor 
        if j>=1
            outVar(:,j) = [yM(j+1:end,i);zeros(j,1)];
        elseif j<0
            jm = -j;            
            if j == -1
                outVarNZ      = outVarN;
            else
                outVarNZ      = ([char(deblank(outVarN)),'(-', num2str(jm-1),')']);
            end
            if find(strcmp(cellstr(char(Model.MulHTEpar.SpyMc)),outVarNZ));
                MulHTEpar.DemeanDeltaW = MulHTEpar.DemeanDeltaW - 1;
                MulHTEpar.SpyMc = [cellstr(MulHTEpar.SpyMc);outVarNZ];
            else
                outVarZ = [outVarZ,[zeros(jm,1);yM(1:end-jm,i)]];
            end
        end
    end
   
    outVar       = outVar(1+wnd:end-hor,:);
    yMj(:,i)     = yM(hor + wnd+1:end,i);
    yMspecT(:,i) = yM(1+wnd:end-hor,i);
    

    
    n = size(outVar,1);
     
    % Compute Nonlinear Impulse Response
    
    switch Model.PScore
    case 'Oprob'
         [Gamma,V_Gamma,V,fit,fit1,GammaPar,GammaParCum,~,~,dp0,dps,TestData,~,VarLogit,~] =Multi_HTE_Oprob(outVar,X,actual,phat,...
                                                                                    score,Omega,xb,cut,zp,level,HTSampDates,MulHTEpar);
         [D,~]  = Actual2D(actual,level);
         hdot = [];
     case 'Probit'         
         [Gamma,V_Gamma,V,hdot,score,dp0,dps]   = Multi_HTE_Probit(outVar,X,actual,phat,Omega,zp,effnumlev,par,HTSampDates,MulHTEpar);
         D    = actual;
         TestData = [];
     end
    
     
    %Compute Cumulated Response (for Level IP)
    
    GammaNC            = Gamma; 
 
    GammaNC      = reshape(GammaNC',size(outVar,2),numlev-1);
    GammaCumNC   = cumsum(GammaNC);

    V_GammaCumNC = zeros(hor,numlev-1);    
    e = triu(ones(hor,hor))';
    for j = 1:numlev-1;
        for ic = 1:hor;            
                e1 = e(ic,:);
                %compute standard errors at horizon j of cumulated response
                V_GammaCumNC(ic,j) = sqrt((e1*V(j).Gamma*e1')/n);            
        end
    end



    E       = eye(numlev-1);
    CumMat  = kron(E,e);             % use this to compute cov mat of cumulative coefficients    
    
    %Store Estimators for Reporting
    GammaSTD   = reshape(sqrt(diag(CumMat'*V_Gamma*CumMat)/n),size(outVar,2),numlev-1);
    Gamma      = GammaNC;
    GammaCum   = GammaCumNC;
    V_GammaCum = V_GammaCumNC;       
    
    
    res.g = Gamma;
    res.gs = GammaSTD;
    res.gc = GammaCum;
    res.gcs = V_GammaCum;
    switch Model.PScore
         case 'Oprob'  
            res.gp  = GammaPar;
            res.gpc = GammaParCum;
    end    
    resarry(i)=res;
    
end

% Record Estimation Statistics for Subsequent Diagnostics and Reporting

Model.yM             = yMj;
Model.yMFit          = yMFit;
Model.DataD          = DD; %Data for descriptive Stats
Model.Diag.yps       = yps; %Data for fit plots
Model.Diag.phatps    = phatps; %Data for fit plots
Model.DVarN          = DVarN;
Model.Diag.y         = y;
Model.Diag.yMspecT   = yMspecT;
Model.Diag.Ytest     = Ytest;
Model.Diag.X         = X;
Model.Diag.Xtest     = Xtest; %Data for SpecTests
Model.Diag.XVarN     = XVarN;
Model.Diag.D         = D;
Model.Diag.phat      = phat;
Model.Diag.TestData  = TestData;
Model.Diag.dp0       = dp0;
Model.Diag.dps       = dps;
Model.Diag.numpar    = numpar;
Model.Diag.VarLogit  = VarLogit;
Model.Diag.score     = score;
Model.Diag.hdot      = hdot;
Model.Diag.nlik      = nlik;
Model.Diag.n         = n;
Model.Diag.EstStart  = datestr(EstSampDates(1,:));
Model.Diag.EstEnd    = datestr(EstSampDates(end,:));
Model.Diag.HTStart   = datestr(HTSampDates(1,:));
Model.Diag.HTEnd     = datestr(HTSampDates(end,:));
Model.Diag.HTSampDates = HTSampDates;
Model.Diag.par       = par;
Model.Diag.cut       = cut;
Model.Diag.stde      = stde;
Model.Diag.tstat     = tstat;
Model.Diag.pva       = pval;
Model.Diag.Lik       = Lik;
Model.Diag.LR        = LR;
Model.Diag.pvLR      = pvLR;
Model.Diag.fit       = fit;
Model.result         = resarry;
Model.fit            = fit;
Model.fit1           = fit1;


switch Model.PScore
    case 'Multinom'    
        Model.Diag.effnumlev = effnumlev;
        Model.Diag.levInd    = levInd;
        Model.Diag.pInd      = pInd;
end

return

