function Model = SetGenParam

Model = struct('Type','','numlev',''); 

%Impulse response Type
Model.PlotType          = 'Cumulative';        % Cumulative, Individual, cumulation method is determined by DemeanMethod
%Model.PlotType          = 'Individual';

%Set General Parameters 
Model.numlev            = 5;         %chose if up/down (3) or -.5,-.25,0,.25.5 (5). Set to 2 for FSW models
Model.outcDemean        = true;      %Demean Outcome variables 
Model.DemeanMethod      = 'FirstDiff';    %two sided moving average ='MoveAv', one sided 'OneAv', full sample mean = 'SampAv'
Model.DemeanFrqLow      = (2*pi)/(32*3); % 96 = 8 years on monthly data
Model.DemeanFrqHigh     = (2*pi)/(6*3);  % 18 = 1 1/2 years on monthly data
Model.DemeanWindow      = 12;
Model.SeasonalDemean    = false;      %obtains outcome variables as residuals of projection on month dummies
Model.Rep25             = true;      %only report +/- .25% changes 
Model.RepNeg25          = false;     %only report -.25 changes
% Horizon for Impulse Response Function
Model.ImpHorizon        = 24;

Model.ReportFFED        = false;     % only report results for FFED

%Parameters controlling Multi_HTE_Oprob
MulHTEpar.Truncate      = true;      % eliminate observations with low p-score prob from sample average
MulHTEpar.Trimm         = false;     % bound  p-score phat below threshold
MulHTEpar.TrimmThs      = .025;      % p-socre lowerbound
MulHTEpar.TruncThs      = .025;      % p-score truncation point
MulHTEpar.Average       = false;     % averge treatments for Up/Down effects in numlev=5 case
MulHTEpar.DemeanDelta   = true;      % subtracts average of delta weights to 
MulHTEpar.DemeanDeltaW  = 0;        % number of lags to include in demeaning of Delta
MulHTEpar.DemeanDeltaL  = false;     % include level variable
MulHTEpar.CovMethod     = 'NW';   % Chose 'NW' for Newey West, 'White' for White standard errors

Model.MulHTEpar         = MulHTEpar;



% Compute Parametric Impulse Response
Model.ParImp           = false;       %ture for parametric approximation
Model.ImpArOrd         = 13;          %Order of the approximating AR polynomial

% run models unconditionally
Model.CondInf          = false;

%Sample Start and End Date
Model.Start             = '1-Jan-1989';  
Model.End               = '31-Dec-2007';
%Sample for p-score estimation
Model.PsStart           = Model.Start;             
Model.PsEnd             = Model.End;
%Sample for policy response estimation
Model.HTStart           = Model.Start;
Model.HTEnd             = Model.End;

%Significance level for confidence bands
Model.ImpRespSigLev     = .1;

% Number of periods lead for outcome variable (to account for lagged
% recording etc
Model.Lead              = 0;

% regression based specification test of the p-score model
% if set to false then a GMM based test is carried out
Model.ResetTest         = false;   % use regression based spec tests
Model.SpecTestWhite     = true;   % use White Standard Errors for Spec Tests
Model.SpecTestBS        = false;   % used Wild Bootstrap to compute p-values for Spec tests
Model.BSRep             = 10000;



if Model.ImpRespSigLev == 0.05;
    Model.ImpRespCrit  = 1.96;
elseif Model.ImpRespSigLev == 0.1;
    Model.ImpRespCrit  = 1.64;
elseif Model.ImpRespSigLev == 0.2;
    Model.ImpRespCrit  = 1.2816;
else
    error('Significance Level not supported');
end

%Pscore estimator Oprob, Multinom, SieveReg, LocProj, MeanDiff
Model.PScore = 'Oprob';

%restrict impulses for up and down changes to be of same magnitude but
%opposiste sign
Model.LinRes =    false;                % only valid for non-linear pscore models
Model.LinResTyp = 'sym';                 % 'sym'=symmetry between +/- moves. 'asymlin' linearity of - and + moves separately

%VAR parameters
Model.VARLags = 12;
Model.VARBootstrapReps = 2000;
Model.VARCumCPI        = true;       %set this flag to compute levels from %changes of CPI
Model.VARSmoothPCOM    = false;       %set this flag to generate smooted differences of PCOM variable
Model.VARReportVARImp  = false;       % set this flag to true if want to report conventional
                                     % VAR impulse responses. false
                                     % generates VAR policy shocks and
                                     % regresses the shocks on Outcome
                                     % variables to estimate impulse
                                     % responses indirectly as in Cochrane
                                     % and Piazzesi
                                     
                                     
 %Multinomial Parameters
 Model.MultiNomQEonly   = false;
 Model.MultiNomQE       = false;     % estimate the multinomial model with QE policy variable
 Model.RepQE            = false;     % only report impulse response for QE shocks

 %Print parameters                                    
 Model.PlotGraphs     = false;            % Default do not plot graphs
 Model.YCSummaryColor = true;             % print summary YC graphs in B&W
 Model.PrintOr        = 'Portrait';       % Choose Landscape or Portrait for pdf output
 Model.Plot1StdE      = false;            % Set true to plot 1 STDE bands as dotted line
 Model.SlideMode      = false;
 Model.PlotSameY      = false;            % use same Y scale on all plots

                                     
% Define Macro Variable for Fit plot to display macro trends


Model.FitMacroSmooth    = true;  %use 2 sided smoothed version of IP
Model.NumFitSmooth      = 6;


return