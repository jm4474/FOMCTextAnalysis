function  [MonthData,MonthColHead] = MergePS1(MonthData,MonthColHead,PS1data,PS1colh,Model,PSVarNType)


if PSVarNType == 1
    AddVarN = intersect(PS1colh,Model.ProScorVarN1)';
    [sx,isxa,~] = setxor(AddVarN,MonthColHead); % only add variables that are not already in MonthColHead
    AddVarN     = AddVarN(isxa);
    y    = zeros(length(PS1data),length(AddVarN));
    
    for i=1:length(AddVarN);
        idv = strcmp(PS1colh,AddVarN(i));
        if idv*ones(length(idv),1)>0 
            y(:,i) = PS1data(:,idv);                
        end
    end

    if Model.VARCumCPI
            CPIInd        = strcmp(Model.ProScorVarN1,Model.CPI);
            y(:,CPIInd)  = cumprod(y(:,CPIInd)/100+1); %reconstruct price level from monthly rate data
    end
    [~,LogInd,~] = intersect(AddVarN,Model.VARLogTransList,'R2012a');
    y(:,LogInd)  = log(y(:,LogInd))*100; % measure in % rather than in rate form; 
    % only take differences of variables not excluded for this operation
    [~,DiffInd]  = setdiff(AddVarN,Model.VARNoDiffList,'R2012a');
    y1           = lag(y,1);    
    y(:,DiffInd) = (y(:,DiffInd)-y1(:,DiffInd));
    
    if isfield(Model,'VARPercTransList')
        [~,PercInd,~] = intersect(AddVarN,Model.VARPercTransList,'R2012a');            
        y(:,PercInd) = y(:,PercInd)./y1(:,PercInd);
    end
    %Only lag values not excluded for this operation
    [~,LagInd]   = setdiff(AddVarN,Model.VARNoLagList,'R2012a');
    y(:,LagInd)  = lag(y(:,LagInd),1);
    MonthColHead = [MonthColHead,AddVarN'];
elseif PSVarNType == 2    
    y    = zeros(length(PS1data),length(Model.ProScorVarN2));
    for i=1:length(Model.ProScorVarN2);
            y(:,i) = PS1data(:,strcmp(PS1colh,Model.ProScorVarN2(i)));    
    end    
    MonthColHead = [MonthColHead,Model.ProScorVarN2'];
    y            = lag(y,1);
end



 

Myear     = MonthData(:,strcmp(MonthColHead,'Year'));
Mmonth    = MonthData(:,strcmp(MonthColHead,'Month'));
Mday      = ones(length(Myear),1);

ycol      = strcmp(PS1colh,'Year');
mcol      = strcmp(PS1colh,'Month');

PSyear    = PS1data(:,ycol);
PSmonth   = PS1data(:,mcol);
PSday     = ones(length(PSyear),1);

Md        = datenum(Myear,Mmonth,Mday);
Pd        = datenum(PSyear,PSmonth,PSday);

k         = size(y,2);
MonthData = [MonthData,zeros(length(MonthData),k)];
[~,ia,ib] = intersect(Md,Pd);

MonthData(ia,end-k+1:end) = y(ib,:);


return