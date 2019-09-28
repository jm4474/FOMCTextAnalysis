clc;
clear;
%GenerateMonthlyData_Script;

P.Type              = 'Macro_OPF2';
P.DemeanMethod      = 'FirstDiff'; 
%P.Start             = '31-Dec-1969';  
%P.End               = '31-Jan-1999';
%P.PsStart           = '31-Dec-1969';  %p-score estimation sample
%P.PsEnd             = '31-Dec-1996';
%P.HTStart           = '31-Dec-1969';  %response estimation sample 
%P.HTEnd             = '31-Jan-1999';
P.numlev            = 5;             % number of distinct policy choices
Horizon             = 24;            % length of IRF
zp                  = 0;             % Value of neutral policy, response are relative to this choice


% Outcome variable data file
P.responseVarfn 	= 'CEE_Macro Data_2012.mat';  
% Policy Model Datafile
P.PolicyModelfn     = 'OPF2_PScore_RepData.mat';     

P.CrisisDate          = '1-Sep-2006';

% Sample period
if ~isfield(P,'Start')
   P.Start             = '31-Jul-1989';
end
if ~isfield(P,'End')
    P.End               = '30-Sep-2009';
end
if ~isfield(P,'ImpRespSigLev')
    P.ImpRespSigLev     = .05;
end
%Sample for p-score estimation
P.PsStart           = P.Start;             
P.PsEnd             = '31-Jul-2005';
%Sample for policy response estimation
P.HTStart           = P.Start;
P.HTEnd             = '30-Jul-2007';


%% Specification of Outcome variables 
%--------------------------------------------------------------------------
if ~isempty(strfind(P.Type,'Macro_'))
        P.RespType = 'MacroVAR';       %controls whether vars are logs or levels before differencing
        Sy             = [%'Trend          '
                          'FFED           '; %effective federal funds rate
                          'PCEH           '; %PCE headline inflation
                          'IP             ';
                          'UNRATE         '; %unemployment rate
                          ];
                          
elseif ~isempty(strfind(P.Type,'YC_'))
        P.RespType = 'YC';
        Sy             = ['RIFLGFCM03';'RIFLGFCY01';'RIFLGFCY02';'RIFLGFCY10'];
        Sy             = [Sy;          'RIFSPFF   '];
end



if datenum('31-Dec-2007') >= datenum(P.End)
    P.VARLogTransList = ['PCEH';'IP  ' % provide list of variables to which a log transform is to be applied
                             ]; 

else
    P.VARLogTransList = ['PCEH';'IP  ' % provide list of variables to which a log transform is to be applied
                             ];
end
    

%-------------------------------------------------------------------------
%% Discretization of policy variable
%-------------------------------------------------------------------------

% Select if policy model is estimated for up-down or .25% increments
if P.numlev == 3 && ~P.MultiNomQEonly
    P.level             = [-.25,0,.25]';
    P.zp                = 2; %picks level element around which output is normalized
elseif P.numlev == 2 && P.MultiNomQEonly
     P.level            = [0,.25]';
    P.zp                = 1;
elseif P.numlev == 2 && ~P.MultiNomQEonly
     P.level            = [-.25,0]';
    P.zp                = 2;    
elseif P.numlev == 5
    P.level             = [-.5, -.25,0,.25,.5]';
    P.zp                = 3; %picks level element around which output is normalized
elseif P.Linear
    P.level             = [0, .25];
    P.zp                = 1;
else
    error ('Numlev not supported');
end


%-------------------------------------------------------------------------
%% P-score Model Covariate definitions
%-------------------------------------------------------------------------


% Variable selection
% Spy = dependent variable for policy model
% Spx = covariates for policy models
% Spx1 = additional covariates for policy model
% SpxT = technical control variables for policy model
% Sy  = outcome variables for impulse response



Spx                 = ['DEAJKold        ';....
                      ];      


 
P.InteractList      = [];
Spx1                = [];
Spx2                = [];
SpxSqList           = [];                 %squared controls
SpxLagList          = [];                 %lagged controls
Spy                 = 'Target Change   '; %dependent variable in policy model

%Define general covariates - modified for specific models as needed

SpxMD =   ['month2          ';'month3          ';'month4          ';...
           'month5          ';'month6          ';'month7          ';'month8          ';...	
           'month9          ';'month10         ';'month11         ';'month12         '];
SpxFED =  ['r               ';...                                
           'LastChange      ';...
           'LastCFOMC       ';
           'Scale           ';
           'FOMC Meetings   '];
     

if datenum(P.PsEnd)<datenum('31-Dec-2000')
    %include 9/11 and Y2K dummies if sample period includes these dataes
    SpxT                 = [SpxFED;SpxMD];   
elseif datenum(P.PsEnd)<datenum('31-Aug-2001')
    SpxT                 = [SpxFED;'DY2K            ';SpxMD];   
else
    SpxT                 = [SpxFED;'DY2K            ';'D911            ';SpxMD];   
end


switch P.Type
    case {'YC_OPT1','Macro_OPT1'}
         Spx                 = [
                                ];                 
         Spx1                = ['PCEH            ';'UNRATE          '];                            
         P.InteractList  = [];

    case {'YC_OPT2','Macro_OPT2'}
         %Covariates for linear regression model model                           
         Spx                 = SpxT;
         Spx1                = ['PCEH            ';'UNRATE          ';'PCEH(-1)        ';'UNRATE(-1)      '];
         SpxLagList          = [];                  


    % Models with Hamilton Fix replace earlier models without fix
   case {'YC_OPF1','Macro_OPF1'}
         Spx                 = [Spx;SpxT];
         P.PolicyModelfn2    = 'NBER_dummy.mat';                                    
         
    case {'YC_OPF2','Macro_OPF2'} %Hamilton Fix models, introduced 2014_05_01
         %Covariates for linear regression model model 
         %delta_exp = Hamilton expectation correction measure
         Spx                 = [Spx;SpxT];
         Spx1                = ['PCEH            ';'UNRATE          ';'PCEH(-1)        ';'UNRATE(-1)      '];
         SpxLagList          = [];
                                
end

%Data Transform definitions for P-score covariates
P.SpxFirstDiffList      = [];   %take first differences of these data - not needed here because data are already in required form
P.SpxPredictorLagList   = [];   %lag these variables by one period - not needed here because data are already in required form
                            
%if ~isempty(SpxLagList)                            
%    SpxL  = TransformLagNames(SpxLagList);                            
%else
%    SpxL  = [];
%end

%-------------------------------------------------------------------------
% convert variable names into cell arrays
% Load variable names into control structure for data load
%-------------------------------------------------------------------------

P.OutcomeVarN  = cellstr(Sy);
if ~isempty(Spy)
    P.ProScorDepVarN = cellstr(Spy);
else    
    P.ProScorDepVarN = [];
end
if ~isempty(Spx)
    P.ProScorVarN = cellstr(Spx);
else
    P.ProScorVarN = [];
end
if ~isempty(Spx1)
    P.ProScorVarN1 = cellstr(Spx1);
end
if ~isempty(Spx2)
    P.ProScorVarN2 = cellstr(Spx2);
end
if ~isempty(SpxLagList)
    P.SpxLagList   = SpxLagList;
end
if ~isempty(SpxSqList)
    P.SpxSqList   = SpxSqList;
end

%-------------------------------------------------------------------------
% Load Data accoring to model defintions
%-------------------------------------------------------------------------

[~,Ds.Inp] = LoadDataMonthly_VerifyJBES(P);
% extract data for estimation

formatOut = 'mm/dd/yyyy';
date_str  = cellstr(datestr(Ds.Inp.SampDat,formatOut));
Start = datestr(Ds.Inp.SampDat(1,:));                                % beginning of data
End   = P.PsEnd;      


y = Ds.Inp.yM; %response variables
D = Ds.Inp.y;  %p-score dependent variable
X = Ds.Inp.X;  %p-score covariates

% Scale variables in percentage point by 100
% y = y.*repmat([1 100 100 1],[size(y,1),1]);

%-------------------------------------------------------------------------
%% Run Model Estimation
%-------------------------------------------------------------------------

Ds = DynamicHTE(y,D,zp,X,Horizon,...
                'BoundMethod','Truncate',...        % options: "Trim" "Truncate"
                'BoundThs',0.025,...
                'PScore','Oprob',...                % options: "Oprob" "MNlogit" "Sieve"
                'SieveType','Poly',...              % choice of sieve basis: "Poly" "TriPol" "Spline"
                'SieveOrder',2,...                  % order of polynomials, only works with the option "Sieve"
                'CovMethod','NW',...                % options: "White" "NW"
                'PScoreCovMethod','Hess',...        % options: "Hess" "Outer" "Robust"
                'PredictScore','Standard',...
                'Leads','Level',...                 % options: "Level" "Diff"
                'Detrend',{'PCEH' 'IP' 'UNRATE'},...
                'TrendType','NA',...
                'Scale',[1 100 100 1],...
                'OutcomeVarN',P.OutcomeVarN,...     % Define variable names for program output
                'PScoreVarN',P.ProScorVarN,...
                'Date',date_str,...                 % date string
                'Start',Start,'End',End);
%-------------------------------------------------------------------------
%% Print Results
%-------------------------------------------------------------------------
TabImpulseResponse(Ds,...
                   'Outcomes','all',...
                   'ResponseType','Cumulative',...
                   'Policy',[.25 -.25],...
                   'Interval',6,...
                   'Columns',4,...
                   'Align','c',...
                   'Headers',{'Funds Rate' 'Inflation' 'Indust. Prod.' 'Unem. Rate'},...
                   'Booktabs','off',...
                   'FileName','MasterFile');

PlotImpulseResponse(Ds,...
                    'Outcomes','all',...
                    'ResponseType','Cumulative',...
                    'CI',.90,...
                    'Policy',[.25 -.25],...
                    'BWDisplay','off',...
                    'Orientation','Portrait',...
                    'Columns',2,...
                    'Titles',{'Funds Rate' 'Inflation' 'Indust. Prod.' 'Unem. Rate'},...
                    'Visible','off',...
                    'FileName','MasterFile');

%% Check Numbers
load 'Published_result.mat'
bounded = logical(sum(Ds.Cont.HTEpar.Loc_Bounded,2));
scale = [1 100 100 1];

gc1_diff = [abs(scale(1)*resp(1).gc - Ds.Out.result.gc{1}), abs(scale(1)*resp(1).gcs - Ds.Out.result.gcs{1})]
gc2_diff = [abs(scale(2)*resp(2).gc - Ds.Out.result.gc{2}), abs(scale(2)*resp(2).gcs - Ds.Out.result.gcs{2})]
gc3_diff = [abs(scale(3)*resp(3).gc - Ds.Out.result.gc{3}), abs(scale(3)*resp(3).gcs - Ds.Out.result.gcs{3})]
gc4_diff = [abs(scale(4)*resp(4).gc - Ds.Out.result.gc{4}), abs(scale(4)*resp(4).gcs - Ds.Out.result.gcs{4})]



