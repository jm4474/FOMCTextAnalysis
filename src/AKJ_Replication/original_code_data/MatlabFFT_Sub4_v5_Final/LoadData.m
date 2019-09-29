function Model = LoadData(Model)


level        = Model.level;
numlev       = size(level,1);
Start        = datenum(Model.Start);
End          = datenum(Model.End);
PsStart      = datenum(Model.PsStart);
PsEnd        = datenum(Model.PsEnd);
HTStart      = datenum(Model.HTStart);
HTEnd        = datenum(Model.HTEnd);

TargetRate   = [];

respvfn      = Model.responseVarfn;  %file name for outcome variables
if isfield(Model,'responseVarfn1');
    respvfn1 = Model.responseVarfn1; %file name for additional outcome vars
else
    respvfn1 = [];
end
polmfn       = Model.PolicyModelfn;  %file name for policy model data

[s,y,dy,ind,dyMonth]     = MergeOutcomeVarFiles(respvfn,respvfn1,Start,End);


i  = 1;
yM                          = zeros(length(ind),size(Model.OutcomeVarN,1)); % allocate memory
Ytest                       = zeros(length(ind),size(Model.CombineTestAllOutcomes,1)); % allocate memory
CombineAllOutcomesRemaining = Model.CombineTestAllOutcomes;
DeleteIndex                 = [];
NotFoundIndex               = [];

while i <= max([size(Model.OutcomeVarN,1),size(Model.CombineTestAllOutcomes,1)])
      if i <= size(Model.OutcomeVarN,1)
          iv = strcmp(s.colheaders,Model.OutcomeVarN(i));
          yM(:,i) = y(ind,iv);              %Outcome variables
      end
      if i <= size(Model.CombineTestAllOutcomes,1)
          ivt = strcmp(s.colheaders,Model.CombineTestAllOutcomes(i));          
          if ~isempty(find(ivt==true,1))
              DeleteIndex = [DeleteIndex, i];
              Ytest(:,i) = y(ind,ivt);                     %Outcome variables
          else
              NotFoundIndex = [NotFoundIndex,i];
          end
      end
      i = i+1;
end
CombineAllOutcomesRemaining(DeleteIndex,:) = []; 

Model.LevelRespData = yM;
Model.LevelRespDate = dyMonth;

lcut = 2; %standard values for sample trunction beginning of sample
ucut = 0; % end of sample
% compute changes
switch Model.RespType
    case {'YC'}
        if Model.outcDemean
            if  strcmp(Model.DemeanMethod,'FirstDiff');                
                yM1          = lag(yM,1);    
                yM           = yM-yM1;
                Ytest1       = lag(Ytest,1);    
                Ytest        = Ytest-Ytest1;

            end            
        end          
   case {'MacroVAR'}
        if Model.VARCumCPI
            CPIInd        = strcmp(Model.OutcomeVarN,Model.CPI);
            yM(:,CPIInd)  = cumprod(yM(:,CPIInd)/100+1); %reconstruct price level from monthly rate data
        end
        [~,LogInd,~]      = intersect(Model.OutcomeVarN,Model.VARLogTransList,'R2012a');
        yM(:,LogInd)      = log(yM(:,LogInd)); 
        [~,LogInd,~]      = intersect(Model.CombineTestAllOutcomes,Model.VARLogTransList,'R2012a');
        Ytest(:,LogInd)   = log(Ytest(:,LogInd));        
        if Model.outcDemean
            if strcmp(Model.DemeanMethod,'FirstDiff');                
                yM1       = lag(yM,1);    
                yM        = yM-yM1;
                Ytest1    = lag(Ytest,1);    
                Ytest     = Ytest-Ytest1;
            end
        end
end
%dyMonth      = dyMonth(2:end,:); %closest end of the month calendar date
yM           = yM(lcut:end-ucut,:);
Ytest        = Ytest(lcut:end-ucut,:);
dyMonth      = dyMonth(lcut:end-ucut,:); %closest end of the month calendar date

% Load outcome variable datafile and prepare input data

%if the data for the policy model are at daily frequency -> convert to
%monthly by using data at the end of prior month as predictors for current
%month policy if there is no scheduled meeting. If there is a scheduled
%meeting, use day before meeting announcemnt as predictor for outcome of
%meeting.
if Model.PolicyDataDaily
    % load tab-delimited text file and unpack structure s
    s = importdata('fff_2012_Matlab Input.txt');
    Dailydata = s.data;
    Dailycolheaders = s.colheaders;
    %convert missing values to zeros

    t = isnan(Dailydata(:,13:15));
    datas = t*0+(1-t)*1;
    Dailydata(:,13:15) = datas;
    
    if Model.MultiNomQE
       s      = importdata('qe_dummies_matlab.txt');
       QEdata = s.data;
       QEcolh = s.colheaders;
       [Dailydata,Dailycolheaders] = MergeFFQE(Dailydata,Dailycolheaders,QEdata,QEcolh);
    end
    s      = load('FRB_H151_2012.mat');
    s      = s.s;
    H15data = s.data;
    H15colh = s.colheaders;
    H15data = fillforward(H15data);
    [Dailydata,Dailycolheaders] = MergeFRBH15(Dailydata,Dailycolheaders,H15data,H15colh);

    
    %generate file with monthly observations
    [MonthData,MonthColHead,Dailydata] = ConvertToMonthly(Dailydata,Dailycolheaders,Start,End);
    if isfield(Model,'PolicyModelfn1')
            s       = load(Model.PolicyModelfn1);
            s       = s.s;
            PS1data = s.data;
            PS1colh = s.colheaders;
            PS1data = fillforward(PS1data);
            
             if isfield(Model,'ProScorVarN1')
                [MonthData,MonthColHead] = MergePS1(MonthData,MonthColHead,PS1data,PS1colh,Model,1);                
             end 
% correction notes: there is no need to selectively load the monthly data.
% Always load the entire dataset no matter whether there are ProScorVarN1
% or not
            Model1 = Model;
            Model1.ProScorVarN1 = Model.SpecTestSpxVarN;
            [MonthData,MonthColHead] = MergePS1(MonthData,MonthColHead,PS1data,PS1colh,Model1,1);                
            clear('Model1');
%           end
            %Note: MergePS1 performs data transformations for use as
            %p-score variables. In particular, it takes logs and first
            %differences when so indicated.
    end
    if isfield(Model,'ProScorVarN2')
            s       = load(Model.PolicyModelfn2);
            s       = s.s;
            PS2data = s.data;
            PS2colh = s.colheaders;
            PS2data = fillforward(PS2data);            
            [MonthData,MonthColHead] = MergePS1(MonthData,MonthColHead,PS2data,PS2colh,Model,2);
    end
    if isempty(intersect(MonthColHead,'delta_exp'))
            Model1 = Model;
            Model1.ProScorVarN1 = 'delta_exp';
            [MonthData,MonthColHead] = MergePS1(MonthData,MonthColHead,PS1data,PS1colh,Model1,1);                
            clear('Model1');       
    end
    % Load Target rate from Dailydata
    [TR,DateTR] = FindTargetRate(Dailydata,Dailycolheaders);
    % Merge with Monthly Data
    [MonthData,MonthColHead] = MergeTargetRate(MonthData,MonthColHead,TR,DateTR);
    
    %compute expectation and surprise variables
    [data,colheaders] = GenSurprise(Dailydata,Dailycolheaders,MonthData,MonthColHead);
    TargetRate        = data(:,strcmp(colheaders,'Target Rate'));
else
    s            = load(polmfn);
    if  isfield(s,'s')
        s            = s.s;
    end
    data         = s.data;
    colheaders   = s.colheaders;
end

% Align dates between outcome file and policy model data

year         = data(:,strcmp(colheaders,'Year'));
month        = data(:,strcmp(colheaders,'Month'));
day          = eomday(year,month);
dx           = datenum([year,month,day]);
[~,ia,ib]    = intersect(dx,dyMonth);   %find common dates in both datasets

%Define Y2K and 911 dummy
[data,colheaders,~] = AddDummy(data,colheaders',dx,ia,'DY2K','1-Dec-1999','31-Jan-2000');
[data,colheaders,~] = AddDummy(data,colheaders,dx,ia,'D891','1-Aug-1991','31-Dec-1991');
[data,colheaders,~] = AddDummy(data,colheaders,dx,ia,'Dp92',[],'31-Dec-1991');
[data,colheaders,~] = AddDummy(data,colheaders,dx,ia,'Da92','1-Jan-1992',[]);
[data,colheaders,~] = AddDummy(data,colheaders,dx,ia,'D911','1-Sep-2001','31-Dec-2001');
colheaders          = colheaders';



%construct futures based predictors using the Hamilton expectation measure
if ~isempty(intersect(colheaders,'delta_exp'))
    % Interact with FOMC dummy for the Hamilton expectation measure
    DEAJKNoFOMC    = data(:,strcmp(colheaders,'delta_exp')).*(ones(size(data,1),1)-data(:,strcmp(colheaders,'FOMC Meetings')));
    data           = [data,DEAJKNoFOMC];
    colheaders     = [colheaders,'DEAJKNoFOMC'];
 
   
    % Interact with FOMC dummy for the Hamilton expectation measure
    DEAJKFOMC      = data(:,strcmp(colheaders,'delta_exp')).*data(:,strcmp(colheaders,'FOMC Meetings'));
    data           = [data,DEAJKFOMC];
    colheaders     = [colheaders,'DEAJKFOMC'];

    DEAJKold       = DEAJKFOMC + DEAJKNoFOMC;
    data           = [data,DEAJKold];
    colheaders     = [colheaders,'DEAJKold'];
    
    DEAJKsq        = DEAJKold.^2;
    data           = [data,DEAJKsq];
    colheaders     = [colheaders,'DEAJKsq'];
end



if Model.Lead ~= 0
    %adjust indices for number of lead periods
    ia       = ia(1:end-Model.Lead,:);
    ib       = ib(1+Model.Lead:end,:);
end


yM           = yM(ib,:);                %match outcome variable dates with available policy model data
SampleDate   = dyMonth(ib,:);
Ytest        = Ytest(ib,:);
%choose policy model variables
if ~isempty(Model.ProScorDepVarN)
    if Model.MultiNomQE
       y        = data(ia,strcmp(colheaders,Model.ProScorDepVarN));              %LHS var in policy model
       yQE      = data(ia,strcmp(colheaders,Model.ProScorQEVarN));
    else
       y        = data(ia,strcmp(colheaders,Model.ProScorDepVarN));              %LHS var in policy model
    end
end


i  = 1;
ProScorVarN            = Model.ProScorVarN;
SpecTestSpxVarN        = Model.SpecTestSpxVarN;
if isfield(Model,'ProScorVarN1')
   if ~isempty(intersect(Model.ProScorVarN,'DEAJKNoFOMC'))
      %if interacted variable is persent in model delete the non-interacted
      %var to avoid multicollinearity
      ProScorVarN = [ProScorVarN;setdiff(Model.ProScorVarN1,'delta_exp')];
   else
      ProScorVarN = [ProScorVarN;Model.ProScorVarN1];
   end
   Model.ProScorVarN = ProScorVarN;
end
if isfield(Model,'ProScorVarN2')
   ProScorVarN = [ProScorVarN;Model.ProScorVarN2];
   Model.ProScorVarN = ProScorVarN;
end

X     = zeros(length(ia),size(ProScorVarN,1)); % allocate memory
Xtest = zeros(length(ia),size(SpecTestSpxVarN,1)); % allocate memory


if isfield(Model,'SpxSqList')
    idsq = strcmp(colheaders,Model.SpxSqList);
    if ~isempty(find(idsq==true,1))
        data = [data,data(:,idsq).^2];
        colheaders  = [colheaders, [Model.SpxSqList,'sq']];
        ProScorVarN = [ProScorVarN;[Model.SpxSqList,'sq']]; 
        Model.ProScorVarN = ProScorVarN;
    end    
end


if isfield(Model,'SpxLagList')
    for il = 1:size(Model.SpxLagList,1);
        idsq = strcmp(colheaders,cellstr(Model.SpxLagList(il,:)));
        if ~isempty(find(idsq==true,1))
            data = [data,lag(data(:,idsq),1)];
            colheaders  = [colheaders, [deblank(Model.SpxLagList(il,:)),'(-1)']];
            ProScorVarN = [ProScorVarN;[deblank(Model.SpxLagList(il,:)),'(-1)']]; 
        end
    end
    Model.ProScorVarN = ProScorVarN;
end


if isfield(Model,'SpxLagOnlyList')
    for il = 1:size(Model.SpxLagOnlyList,1);
        idsq = strcmp(colheaders,cellstr(Model.SpxLagOnlyList(il,:)));
        if ~isempty(find(idsq==true,1))
            data = [data,lag(data(:,idsq),1)];
            colheaders  = [colheaders, [deblank(Model.SpxLagList(il,:)),'(-1)']];
            ProScorVarN = [ProScorVarN;[deblank(Model.SpxLagList(il,:)),'(-1)']]; 
        end
    end
    Model.ProScorVarN = ProScorVarN;
end


if isfield(Model,'SpecTestSpxLagList')
    for il = 1:size(Model.SpecTestSpxLagList,1);
        %check if already added lag before
        idlag = strcmp(colheaders, [deblank(Model.SpecTestSpxLagList(il,:)),'(-1)']);
        if isempty(find(idlag==true,1))
            idsq = strcmp(colheaders,cellstr(Model.SpecTestSpxLagList(il,:)));
            if ~isempty(find(idsq==true,1))
                data = [data,lag(data(:,idsq),1)];
                colheaders      = [colheaders, [deblank(Model.SpecTestSpxLagList(il,:)),'(-1)']];
            else
                error('Lagged Pscore Covariate not found');
            end                    
        end
        SpecTestSpxVarN = [SpecTestSpxVarN',[deblank(Model.SpecTestSpxLagList(il,:)),'(-1)']]';            
    end
    Model.SpecTestSpxVarN = SpecTestSpxVarN;
end

%Load data into p-score covariate matrix
while i <= max([size(ProScorVarN,1),size(SpecTestSpxVarN,1),size(CombineAllOutcomesRemaining,1)])
      if i <=size(ProScorVarN,1) 
         iv  = strcmp(colheaders,ProScorVarN(i));
          if isempty(find(iv==true,1))
              if strcmp('Cons',ProScorVarN(i))
                 X(:,i) = ones(length(X),1);
              end
          else
              X(:,i) = data(ia,iv);                     %Outcome variables
          end
      end
      if i <= size(SpecTestSpxVarN,1)
         ivt = strcmp(colheaders,SpecTestSpxVarN(i));          
          if isempty(find(ivt==true,1))
              if strcmp('Cons',SpecTestSpxVarN(i))
                 Xtest(:,i) = ones(length(X),1);
              end
          else
              Xtest(:,i) = data(ia,ivt);                     %Outcome variables
          end
      end
      if i <= size(CombineAllOutcomesRemaining,1)
         ivt = strcmp(colheaders,CombineAllOutcomesRemaining(i));          
          if ~isempty(find(ivt==true,1))  
              YtestTemp                   = data(ia,ivt);   %Load p-score cov into outcome test vector for 'All Outcomes' test              
              Ytest(:,NotFoundIndex(1,1)) = [YtestTemp(2:end,:);0]; %Lead one period to undo lagging in spectest routine
              NotFoundIndex(:,1)          = [];             %remove index from list
          end
      end
      i = i+1;
end




%Define Crisis Dummy and interaction terms for p-score
if isfield(Model,'InteractVar') || isfield(Model,'CrisisDummy')
    if isfield(Model,'CrisisDummy')
        [X,ProScorVarN,Cdum] = AddDummy(X,ProScorVarN,dyMonth,ib,'Crisis',Model.CrisisDate,[]);
        cJ          = size(ProScorVarN,1)-1;
    elseif isfield(Model,'InteractVar')
        iav  = strcmp(ProScorVarN,Model.InteractVar);      
        if sum(iav)> 0
            Cdum = X(:,iav);
        else
            error('Interaction Variable not found in Pscore')
        end        
        cJ          = size(ProScorVarN,1);
    end
    for i=1:cJ
        if find(strcmp(Model.InteractList,ProScorVarN(i)))
           if isfield(Model,'CrisisDummy')
                ProScorVarN = [ProScorVarN;[char(ProScorVarN(i)),'XCrisis']];
           elseif isfield(Model,'InteractVar')
               % if isempty(find(strcmp(ProScorVarN(i),Model.InteractVar)))
                    %dont interact variable with itself
                    ProScorVarN = [ProScorVarN;[char(ProScorVarN(i)),'X',Model.InteractVar]];
               % end
           end
           X           = [X, X(:,i).*Cdum];
           X(:,i)      = X(:,i).*(ones(size(X,1),1)-Cdum);
        end
    end
Model.ProScorVarN = ProScorVarN;    
end

% Compress fed-policy variable to up-down-nothing if numlev==3
if numlev == 3
        y    = y.*(abs(y)<=.25)+.25*(y>.25)-.25*(y<-.25); 
elseif numlev == 5
        y    = y.*(abs(y)<=.5)+.5*(y>.5)-.5*(y<-.5); 
elseif numlev == 2
        y    = 0*(y>=0)-.25*(y<0);
end

[~,ic,id]    = intersect(dx,Model.LevelRespDate);   %find common dates in both datasets


%count number of different policy actions for book-keeping
if ~isempty(TargetRate)
    Model.TargetRate = TargetRate(ic,:);
    Model.LevelRespData = Model.LevelRespData(id,:);
    Model.LevelRespDate = Model.LevelRespDate(id,:);
    Model.CM5   = sum(y<=-.5);
    Model.CM25  = sum(y==-.25);
    Model.C0    = sum(y==0);
    Model.C25   = sum(y==.25);
    Model.C5    = sum(y==.5);
end



%if isfield(Model,'SpxLagList') always cut sample to make sample size equal
%across models
   yM         = yM(2:end,:);
   y          = y(2:end,:);
   X          = X(2:end,:);
   Xtest      = Xtest(2:end,:);
   Ytest      = Ytest(2:end,:);
   SampleDate = SampleDate(2:end,:);
   Model.LevelRespData = Model.LevelRespData(2:end,:);
   Model.LevelRespDate = Model.LevelRespDate(2:end,:);
   Model.TargetRate    = Model.TargetRate(2:end);

%end

if det(X'*X) == 0
    error('DataLoad: Pscore covariate matrix singular');
end


Model.yM      = yM;
Model.y       = y;
Model.X       = X;
Model.Xtest   = Xtest;
Model.Ytest   = Ytest;
Model.SampDat = SampleDate;
SD            = SampleDate;
Model.MulHTEpar.ProScorVarN = ProScorVarN; 


if PsStart>=Start && PsEnd<=End
    Model.PsSampDat = SD(SD>=PsStart & SD<=PsEnd,:);
else
    error('Dates for P-score estimation must be within sample period');
end
if HTStart>=Start && HTEnd<=End
    Model.HTSampDat = SD(SD>=HTStart & SD<=HTEnd,:);
else
    error('Dates for P-score estimation must be within sample period');
end   




return