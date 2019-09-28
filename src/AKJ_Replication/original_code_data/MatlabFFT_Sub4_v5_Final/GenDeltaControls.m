function Z = GenDeltaControls(X,MulHTEpar)   % select detrending controls for delta


ProScorVarN = MulHTEpar.ProScorVarN;
SpyMc       = char(MulHTEpar.SpyMc);
SpyMc       = cellstr(intersect(SpyMc,SpyMc,'rows')); %remove double entries from SpyMc to avoid multicollinearity

if isempty(char(SpyMc))
    k       = 0;
else
    k           = size(SpyMc,1);
end
if isfield(MulHTEpar,'Z');
    Z       = [MulHTEpar.Z,zeros(length(X),k)];
    if MulHTEpar.DemeanDeltaL
        wnd     = MulHTEpar.DemeanDeltaW+1;
    else
        wnd     = MulHTEpar.DemeanDeltaW;
    end
else
    Z          = zeros(length(X),k);
    wnd        = 0;
end
for i = 1:k
   ind = strcmp(ProScorVarN,cellstr(SpyMc(i,:)));
   if strcmp(cellstr(SpyMc(i,:)),'Cons')
       Z(:,wnd+i) = ones(length(X),1);
   elseif strcmp(cellstr(SpyMc(i,:)),'Trend')
       Z(:,wnd+i) = (1:length(X))';
   elseif ~(sum(ind)==0)       
       Z(:,wnd+i) = X(:,ind);       
   else
       error('GenDeltaControls: Control variable not found in P-score covariates');
   end   
end

return
