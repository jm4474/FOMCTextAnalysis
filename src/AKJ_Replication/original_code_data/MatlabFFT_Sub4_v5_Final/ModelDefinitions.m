function Model = ModelDefinitions(Model)
% This function defines variables used in the policy models and as outcome
% variables for various specifications. Additional models can be defined here
% There are four policy models PS1, PS2, PS1_Br and PS2_Br. PS1 only
% contains a measure of the expected policy change while PS2 adds
% additional covariates. _Br adds a structural break in 1994
% The four policy models are combined with two sets of outcome variables,
% one the yield curve, the other a set of general macro variables.
% Combined this leads to a total of 8 different specifications

InteractVar               = [];
Spx2                      = [];
Model.CrisisDate          = '1-Sep-2006';
Model.ExcludeOutcomeList  = [];



if strcmp(Model.Type,'YC_FSW') || strcmp(Model.Type,'Macro_FSW')
    if ~(Model.LinRes==false && Model.numlev==2)
        error('Incompatible Type, LinRes and numlev values, set numlev=2');
    end
end

if strcmp(Model.Type,'YC_CEE_VAR') || strcmp(Model.Type,'Macro_CEE_VAR')
    if ~(Model.LinRes==false && Model.numlev==2)
        error('Incompatible Type, LinRes and numlev values, set numlev=2');
    end
else
    if Model.VARReportVARImp
        Model.VARReportVARImp = false;
    end
end


% Sample period
if ~isfield(Model,'Start')
   Model.Start             = '31-Jan-1989';
end
if ~isfield(Model,'End')
    Model.End               = '31-Dec-2007';
end
if ~isfield(Model,'ImpRespSigLev')
    Model.ImpRespSigLev     = .05;
end




% Impulse response Type
switch Model.PScore
    case{'Oprob', 'Multinom', 'Probit','Unweighted'}
        Model.ImpType           = 'NL';
        Model.Linear            = false;
    case{'LocProj'}
        Model.ImpType           = 'L';
        Model.Linear            = true;
end



if ~isempty(strfind(Model.Type,'Macro_'))
        Model.RespType = 'MacroVAR';       %controls whether vars are logs or levels before differencing
        Sy             = ['FFED           '; %effective federal funds rate
                          'PCEH           '; %PCE headline inflation
                          'IP             ';
                          'UNRATE         '; %unemployment rate
                          ];
        
        Model.responseVarfn      = 'CEE_Macro Data_2012.mat';                   
        Model.responseVarfn1     = 'FRB_H151_2012.mat';   
        Model.VARPCOM            = 'PZRAW'; %Defines the commodity price variable
        Model.CPI                = '';
        
     
elseif ~isempty(strfind(Model.Type,'YC_'))
        Model.PlotSameY = true; % use same scale on all plots
        Model.RespType = 'YC';
        Sy             = ['RIFLGFCM03';'RIFLGFCY02';'RIFLGFCY05';'RIFLGFCY10'];
        Sy             = [Sy;          'RIFSPFF   '];
        Model.responseVarfn = 'FRB_H151_2012.mat';  
end

Model.FitMacroVarN = cellstr('IP');

% Policy Model Datafile

Model.PolicyModelfn     = 'fff_2012_Matlab Input.txt';     
Model.PolicyModelfn1    = 'CEE_Macro Data_2012.mat';        
Model.PolicyDataDaily   = true; 
Model.VARPCOM           = 'PZRAW'; %Defines the commodity price variable
Model.CPI               = '';

if datenum('31-Dec-2007') >= datenum(Model.End)
    Model.VARLogTransList = ['IP             '; % provide list of variables to which a log transform is to be applied
                             'PZRAW          ';
                             'PCEH           '; % PCE headline inflation 
                             'PCE            '; % PCE core inflation 
                             'CE16OV_20110708'];
else
    Model.VARLogTransList = ['IP             '; % provide list of variables to which a log transform is to be applied
                             'PZRAW          ';
                             'PCEH           ';
                             'PCE            ';
                             'CE16OV_20110708'];
end
%Indicate which variables in the macro file not to lag (for MergePS1.m code called in LoadData.m)
Model.VARNoLagList = cellstr('delta_exp       ');
%Indicate which variables in the macro file not to difference (for MergePS1.m code called in LoadData.m)
Model.VARNoDiffList = cellstr('delta_exp       ');


    

% Select if policy model is estimated for up-down or .25% increments
if Model.numlev == 3 && ~Model.MultiNomQEonly
    Model.level             = [-.25,0,.25]';
    Model.zp                = 2; %picks level element around which output is normalized
elseif Model.numlev == 2 && Model.MultiNomQEonly
     Model.level            = [0,.25]';
    Model.zp                = 1;
elseif Model.numlev == 2 && ~Model.MultiNomQEonly
     Model.level            = [-.25,0]';
    Model.zp                = 2;    
elseif Model.numlev == 5
    Model.level             = [-.5, -.25,0,.25,.5]';
    Model.zp                = 3; %picks level element around which output is normalized
elseif Model.Linear
    Model.level             = [0, .25];
    Model.zp                = 1;
else
    error ('Numlev not supported');
end



% Variable selection
% Spy = dependent variable for policy model
% Spx = covariates for policy models
% Sy  = outcome variables for impulse response

Spx1                = [];
SpxSqList           = [];
SpxLagList          = [];
Spy                 = 'actual          '; %dependent variable in policy model

%Define general covariates - modified for specific models as needed
SpxT                 = ['r               ';...                                
                    'LastChange      ';...
                    'LastCFOMC       ';
                    'Scale           ';
                    'FOMC Meetings   ';...
                    'DY2K            ';
                    'D911            ';...
                    'month2          ';'month3          ';'month4          ';...
                    'month5          ';'month6          ';'month7          ';'month8          ';...	
                    'month9          ';'month10         ';'month11         ';'month12         '
                   ];   
Spx                 = ['DEAJKold        ';....
                      ];                   
 
Model.InteractList  = cellstr(['DEAJKold        ';....
             ]);


%}               
switch Model.Type
    case {'YC_OPT1','Macro_OPT1'}
         Spx                 = [
                                ];                 
         Spx1                = ['PCEH            ';'UNRATE          '];                            
         Model.InteractList  = [];
         Spy                 = 'Change';             
    case {'YC_OPT2','Macro_OPT2'}
         %Covariates for linear regression model model                           
         Spx                 = SpxT;
         Spx1                = ['PCEH            ';'UNRATE          '];
         SpxLagList          = ['PCEH            ';'UNRATE          '];                  
         Spy                 = 'Change';                                                
    % Models with Hamilton Fix replace earlier models without fix
   case {'YC_OPF1','Macro_OPF1'}
         Spx                 = [Spx;
                                SpxT];
         Model.PolicyModelfn2    = 'NBER_dummy.mat';                                    
         Spy                 =  'Change';                                     

    case {'YC_OPF2','Macro_OPF2'} %Hamilton Fix models, introduced 2014_05_01
         %Covariates for linear regression model model 
         %delta_exp = Hamilton expectation correction measure
         Spx                 = [Spx;
                                SpxT];
         Spx1                = [
                                'PCEH            ';'UNRATE          '
                                ];                  

         SpxLagList          = ['PCEH            ';'UNRATE          ';...
                                ];
         Spy                 =  'Change';                            
         
    case {'YC_OPT1C','Macro_OPT1C'}
         Spx                 = [
                                ];                 
         Spx1                = ['PCEH            ';'UNRATE          '];                            
         Model.InteractList  = [];
         Spy                 = 'Change';             
         Model.CrisisDummy   = true;                               
         
    case {'YC_OPT2C','Macro_OPT2C'}
         %Covariates for linear regression model model                           
         Spx                 = SpxT;                                
         Spx1                = ['PCEH            ';'UNRATE          '];
         SpxLagList          = ['PCEH            ';'UNRATE          '];                  
         Spy                 = 'Change';                                                
         Model.CrisisDummy   = true;                               
         Model.InteractList  = [];

    case {'YC_OPF1C','Macro_OPF1C'}
         Spx                 = [Spx;
                                SpxT];
         Spy                 =  'Change';                            
         Model.CrisisDummy   = true;   
         
    case {'YC_OPF2C','Macro_OPF2C'}
         Spx                 = [Spx;
                                SpxT];
         Spx1                = [
                                'PCEH            ';'UNRATE          '
                                ];

         SpxLagList          = ['PCEH            ';'UNRATE          ';...
                                ];
         Spy                 =  'Change';                            
         Model.CrisisDummy   = true;   

    case {'YC_PT','Macro_PT'}
         %Covariates for linear regression model model                           
         Spx                 = ['Cons            ';...
                                'r               '
                                ];
         Spx1                = ['PCEH            ';'UNRATE          '];                            
         Spy                 = 'Change';                 
                                                            
    case {'YC_PF1','Macro_PF1'}
         %Covariates for linear regression model model                           
         Spx                 = ['Cons            ';...
                                'r               ';...
                                ];
         Spx1                = ['delta_exp       '];                            
         Spy                 = 'Change';                 
         
   case {'YC_PF2','Macro_PF2'}
         %Covariates for linear regression model model                           
         Spx                 = ['Cons            ';...
                                'r               ';...                                
                                ];
         Spx1                = [
                                'delta_exp       ';... 
                                'PCEH            ';'UNRATE          '
                                ];                            
         Spy                 = 'Change';                 
   case {'YC_PF3','Macro_PF3'}
         %Covariates for linear regression model model                           
         Spx                 = ['Cons            ';...
                                'r               ';...  
                                ];
         Spx1                = [
                                'delta_exp       ';... 
                                'PCEH            ';'UNRATE          '
                                ];                            
         Spy                 = 'Change';                 
         SpxLagList          = ['PCEH            ';'UNRATE          ';...
                               ];

end

SpecTestSpxVarN              = ['DEAJKold        ';'DEAJKsq         ';...
                                'eFFr            ';
                                'r               ';
                                'LastChange      ';...
                                'FOMC Meetings   ';...
                                'PCEH            ';
                                'UNRATE          '
                                ];
Model.SpecTestSpxLagList     = ['PCEH            ';
                                'UNRATE          '
                                ];


CombineTestVarSpx             = ['DEAJKold        ';'DEAJKsq         ';...
                                ];

CombineTestVarYields          = ['RIFLGFCM03      ';'RIFLGFCY02      ';...
                                 'RIFLGFCY05      ';'RIFLGFCY10      '
                                ];
CombineTestAllOutcomes         = ['RIFLGFCM03      ';'RIFLGFCY02      ';...
                                 'RIFLGFCY05      ';'RIFLGFCY10      ';...
%                                 'eFFr            ';...                                 
                                 'FFED            ';...
                                 'IP              ';...
                                 'RIFSPFF         '
%                                 'DEAJKsq         ';...
                                ];                            
                            
                            

                            
if ~isempty(SpxLagList)                            
    SpxL  = TransformLagNames(SpxLagList);                            
else
    SpxL  = [];
end


SpyMc = [Spx;Spx1;Spx2;SpxL];            

% convert variable names into cell arrays
Model.OutcomeVarN  = cellstr(Sy);
Model.SpecTestVarN = cellstr(Sy);
% add Titles for Impulse Prints
Model.OutcomePrintNames = SetPrintNames(Model.OutcomeVarN);
Model.DoReportList      = SetDoNotPrintList(Model.Type,Model.OutcomeVarN,Model.ReportFFED);
if ~isempty(Spy)
    Model.ProScorDepVarN = cellstr(Spy);
else    
    Model.ProScorDepVarN = [];
end
if ~isempty(SpyMc)
    Model.MulHTEpar.SpyMc    = SpyMc;
end
if ~isempty(SpxSqList)
    Model.SpxSqList   = SpxSqList;
end
if ~isempty(SpxLagList)
    Model.SpxLagList   = SpxLagList;
end
if ~isempty(InteractVar)
    Model.InteractVar = InteractVar;
end
if ~isempty(Spx)
    Model.ProScorVarN = cellstr(Spx);
else
    Model.ProScorVarN = [];
end
if ~isempty(Spx1)
    Model.ProScorVarN1 = cellstr(Spx1);
end
if ~isempty(Spx2)
    Model.ProScorVarN2 = cellstr(Spx2);
end
Model.SpecTestSpxVarN            = cellstr(SpecTestSpxVarN);
Model.CombineTestVarSpx          = cellstr(CombineTestVarSpx);
Model.CombineTestVarYields       = cellstr(CombineTestVarYields);
Model.CombineTestAllOutcomes     = cellstr(CombineTestAllOutcomes);
return