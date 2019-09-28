function [Model,Data] = LoadDataMonthly_VerifyJBES(Model)


level        = Model.level;
numlev       = size(level,1);
Start        = datenum(Model.Start);
End          = datenum(Model.End);
PsStart      = datenum(Model.PsStart);
PsEnd        = datenum(Model.PsEnd);
HTStart      = datenum(Model.HTStart);
HTEnd        = datenum(Model.HTEnd);


respvfn      = Model.responseVarfn;  %file name for outcome variables
if isfield(Model,'responseVarfn1');
    respvfn1 = Model.responseVarfn1; %file name for additional outcome vars
else
    respvfn1 = [];
end
polmfn       = Model.PolicyModelfn;  %file name for policy model data

[s,y,~,ind,dyMonth]     = MergeOutcomeVarFiles_VerifyJBES(respvfn,respvfn1,Start,End);


i  = 1;
yM = zeros(length(ind),size(Model.OutcomeVarN,1)); % allocate memory
while i <= size(Model.OutcomeVarN,1)
      iv = strcmp(s.colheaders,Model.OutcomeVarN(i));
      yM(:,i) = y(ind,iv);                     %Outcome variables
      i = i+1;
end



[~,LogInd,~] = intersect(Model.OutcomeVarN,Model.VARLogTransList,'R2012a');
yM(:,LogInd)  = log(yM(:,LogInd)); 

if strcmp(Model.DemeanMethod,'FirstDiff');                
    yM1          = lag(yM,1);    
    yM           = yM-yM1;
end

Model.LevelRespData = yM;
Model.LevelRespDate = dyMonth;

s            = load(polmfn);
if  isfield(s,'s')
    s            = s.s;
end
data         = s.data;
colheaders   = s.colheaders;


% Align dates between outcome file and policy model data

year         = data(:,strcmp(colheaders,'Year'));
month        = data(:,strcmp(colheaders,'Month'));
day          = eomday(year,month);
dx           = datenum([year,month,day]);
[~,ia,ib]    = intersect(dx,dyMonth);   %find common dates in both datasets

TargetRate   = data(:,strcmp(colheaders,'r'));


yM           = yM(ib,:);                %match outcome variable dates with available policy model data
SampleDate   = dyMonth(ib,:);
%choose policy model variables
if ~isempty(Model.ProScorDepVarN)
    y        = data(ia,strcmp(colheaders,Model.ProScorDepVarN));              %LHS var in policy model
end


i  = 1;
ProScorVarN            = Model.ProScorVarN;
SpecTestSpxVarN        = [];
if isfield(Model,'ProScorVarN1')
   ProScorVarN = [ProScorVarN;Model.ProScorVarN1];
   Model.ProScorVarN = ProScorVarN;
end
if isfield(Model,'ProScorVarN2')
   ProScorVarN = [ProScorVarN;Model.ProScorVarN2];
   Model.ProScorVarN = ProScorVarN;
end

X     = zeros(length(ia),size(ProScorVarN,1)); % allocate memory
Xtest = zeros(length(ia),size(SpecTestSpxVarN,1)); % allocate memory

%{
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
%}

%Load data into p-score covariate matrix
while i <= max(size(ProScorVarN,1),size(SpecTestSpxVarN,1))
      if i <=size(ProScorVarN,1) 
         iv  = strcmp(colheaders,ProScorVarN(i));
          if isempty(find(iv==true,1))
              if strcmp('Cons',ProScorVarN(i))
                 X(:,i) = ones(length(X),1);
              end
          else
              if ~isempty(find(strcmp(Model.SpxFirstDiffList,ProScorVarN(i)),1))
                  if ~isempty(find(strcmp(Model.SpxPredictorLagList,ProScorVarN(i)),1))
                      Xstore = lag(data(:,iv),1)-lag(data(:,iv),2); 
                  else
                      Xstore = data(:,iv)-lag(data(:,iv),1); 
                  end
              elseif ~isempty(find(strcmp(Model.SpxPredictorLagList,ProScorVarN(i)),1))
                      Xstore = lag(data(:,iv),1);
              else
                      Xstore = data(:,iv);                     %Outcome variables
              end
              X(:,i)         = Xstore(ia,1);
          end
      end
      if i <= size(SpecTestSpxVarN,1)
         ivt = strcmp(colheaders,SpecTestSpxVarN(i));  
         if ~isempty(find(ivt,1))
            if isempty(find(ivt==true,1))
                  if strcmp('Cons',SpecTestSpxVarN(i))
                     Xtest(:,i) = ones(length(X),1);
                  end
            else
                  Xtest(:,i) = data(ia,ivt);                     %Outcome variables
            end
         else
             error('Spec test variale not found - error in LoadDataMonthly');
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
%}


% Compress fed-policy variable to up-down-nothing if numlev==3
if numlev == 3
        y    = y.*(abs(y)<=.25)+.25*(y>.25)-.25*(y<-.25); 
elseif numlev == 5
        y    = -.25*and((-.25<=y),(y<0))-.5*and((-.5<=y),(y<-.25))+0*(0==y)+.25*and((0<y),(y<=.25))...
                +.5*and((.25<y),(y<=.5))+.5*(y>.5)-.5*(y<-.5); 


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


if isfield(Model,'SpxLagList') %always cut sample to make sample size equal across models
   yM         = yM(2:end,:);
   y          = y(2:end,:);
   X          = X(2:end,:);
   Xtest      = Xtest(2:end,:);
   SampleDate = SampleDate(2:end,:);
   Model.LevelRespData = Model.LevelRespData(3:end,:);
   Model.LevelRespDate = Model.LevelRespDate(3:end,:);
   Model.TargetRate    = Model.TargetRate(3:end);

end



if det(X'*X) == 0
    error('DataLoad: Pscore covariate matrix singular');
end


Data.yM      = yM;
Data.y       = y;
Data.X       = X;
Data.Xtest   = Xtest;
Data.SampDat = SampleDate;
SD           = SampleDate;
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