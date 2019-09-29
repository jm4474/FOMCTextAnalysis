clear;

%Nil Definition of basic control datastructure
MaxTestVar = 12;
pval   = zeros(MaxTestVar,9);
pvalQE = zeros(MaxTestVar,6);

%Code Block to modify default param values 

%%


% NBER Short Sample estimators


Model = SetGenParam;
Model.Type              = 'Macro_OPT1';
Model.Start             = '1-Jan-1989';  
Model.End               = '30-Sep-2009';
Model.PsStart           = '1-Jan-1989';  %p-score estimation sample
Model.PsEnd             = '31-Jul-2005';
Model.HTStart           = '1-Jan-1989';  %response estimation sample 
Model.HTEnd             = '31-Jul-2007';
Model                   = CompMultiImp(Model);
SpecTestTab             = CreateSpecTestTable(Model,[],false);
SpecTestTabSpx          = CreateSpecTestSpxTable(Model,[],false);




Model = SetGenParam;
Model.MulHTEpar.DemeanDelta   = false;  
Model.Type              = 'Macro_OPT1';
Model.Start             = '1-Jan-1989';  
Model.End               = '30-Sep-2009';
Model.PsStart           = '1-Jan-1989';  %p-score estimation sample
Model.PsEnd             = '31-Jul-2005';
Model.HTStart           = '1-Jan-1989';  %response estimation sample 
Model.HTEnd             = '31-Jul-2007';
Model.ReportFFED        = true;
Model                   = CompMultiImp(Model);
SpecTestTab             = CreateSpecTestTable(Model,SpecTestTab,true);


Model = SetGenParam;
Model.MulHTEpar.DemeanDelta   = false;  
Model.Type              = 'YC_OPT1';
Model.Start             = '1-Jan-1989';  
Model.End               = '30-Sep-2009';
Model.PsStart           = '1-Jan-1989';  %p-score estimation sample
Model.PsEnd             = '31-Jul-2005';
Model.HTStart           = '1-Jan-1989';  %response estimation sample 
Model.HTEnd             = '31-Jul-2007';
Model                   = CompMultiImp(Model);
SpecTestTab             = CreateSpecTestTable(Model,SpecTestTab,true);



Model = SetGenParam;
Model.Type              = 'Macro_OPT2';
Model.Start             = '1-Jan-1989';  
Model.End               = '30-Sep-2009';
Model.PsStart           = '1-Jan-1989';  %p-score estimation sample
Model.PsEnd             = '31-Jul-2005';
Model.HTStart           = '1-Jan-1989';  %response estimation sample 
Model.HTEnd             = '31-Jul-2007';
Model                   = CompMultiImp(Model);
SpecTestTab             = CreateSpecTestTable(Model,SpecTestTab,false);
SpecTestTabSpx          = CreateSpecTestSpxTable(Model,SpecTestTabSpx,false);



Model = SetGenParam;
Model.MulHTEpar.DemeanDelta   = false;  
Model.Type              = 'Macro_OPT2';
Model.Start             = '1-Jan-1989';  
Model.End               = '30-Sep-2009';
Model.PsStart           = '1-Jan-1989';  %p-score estimation sample
Model.PsEnd             = '31-Jul-2005';
Model.HTStart           = '1-Jan-1989';  %response estimation sample 
Model.HTEnd             = '31-Jul-2007';
Model.ReportFFED        = true;
Model                   = CompMultiImp(Model);
SpecTestTab             = CreateSpecTestTable(Model,SpecTestTab,true);

Model = SetGenParam;
Model.MulHTEpar.DemeanDelta   = false;  
Model.Type              = 'YC_OPT2';
Model.Start             = '1-Jan-1989';  
Model.End               = '30-Sep-2009';
Model.PsStart           = '1-Jan-1989';  %p-score estimation sample
Model.PsEnd             = '31-Jul-2005';
Model.HTStart           = '1-Jan-1989';  %response estimation sample 
Model.HTEnd             = '31-Jul-2007';
Model                   = CompMultiImp(Model);
SpecTestTab             = CreateSpecTestTable(Model,SpecTestTab,true);


Model = SetGenParam;
Model.Type              = 'Macro_OPF1';
Model.Start             = '1-Jan-1989';  
Model.End               = '30-Sep-2009';
Model.PsStart           = '1-Jan-1989';  %p-score estimation sample
Model.PsEnd             = '31-Jul-2005';
Model.HTStart           = '1-Jan-1989';  %response estimation sample 
Model.HTEnd             = '31-Jul-2007';
Model                   = CompMultiImp(Model);
SpecTestTab             = CreateSpecTestTable(Model,SpecTestTab,false);
SpecTestTabSpx          = CreateSpecTestSpxTable(Model,SpecTestTabSpx,false);


Model = SetGenParam;
Model.MulHTEpar.DemeanDelta   = false;   
Model.Type              = 'Macro_OPF1';
Model.Start             = '1-Jan-1989';  
Model.End               = '30-Sep-2009';
Model.PsStart           = '1-Jan-1989';  %p-score estimation sample
Model.PsEnd             = '31-Jul-2005';
Model.HTStart           = '1-Jan-1989';  %response estimation sample 
Model.HTEnd             = '31-Jul-2007';
Model.ReportFFED        = true;
Model                   = CompMultiImp(Model);
SpecTestTab             = CreateSpecTestTable(Model,SpecTestTab,true);



Model = SetGenParam;
Model.MulHTEpar.DemeanDelta   = false;   
Model.Type              = 'YC_OPF1';
Model.Start             = '1-Jan-1989';  
Model.End               = '30-Sep-2009';
Model.PsStart           = '1-Jan-1989';  %p-score estimation sample
Model.PsEnd             = '31-Jul-2005';
Model.HTStart           = '1-Jan-1989';  %response estimation sample 
Model.HTEnd             = '31-Jul-2007';
Model                   = CompMultiImp(Model);
SpecTestTab             = CreateSpecTestTable(Model,SpecTestTab,true);

%}


Model = SetGenParam;
Model.PlotGraphs        = true;  
Model.Type              = 'Macro_OPF2';
Model.Start             = '1-Jan-1989';  
Model.End               = '30-Sep-2009';
Model.PsStart           = '1-Jan-1989';  %p-score estimation sample
Model.PsEnd             = '31-Jul-2005';
Model.HTStart           = '1-Jan-1989';  %response estimation sample 
Model.HTEnd             = '31-Jul-2007';
Model                   = CompMultiImp(Model);
IRFTabPF2               = Create_ImpulseResponse_Table(Model,[]);
SpecTestTab             = CreateSpecTestTable(Model,SpecTestTab,false);
SpecTestTabSpx          = CreateSpecTestSpxTable(Model,SpecTestTabSpx,false);

%}

Model = SetGenParam;
Model.PlotGraphs        = true;  
Model.MulHTEpar.DemeanDelta   = false;   
Model.Type              = 'Macro_OPF2';
Model.Start             = '1-Jan-1989';  
Model.End               = '30-Sep-2009';
Model.PsStart           = '1-Jan-1989';  %p-score estimation sample
Model.PsEnd             = '31-Jul-2005';
Model.HTStart           = '1-Jan-1989';  %response estimation sample 
Model.HTEnd             = '31-Jul-2007';
Model.ReportFFED        = true;
Model                   = CompMultiImp(Model);
IRFTabPF2               = Create_ImpulseResponse_Table(Model,IRFTabPF2);


Model = SetGenParam;
Model.PlotGraphs        = true;  
Model.MulHTEpar.DemeanDelta   = false;   
Model.Type              = 'YC_OPF2';
Model.Start             = '1-Jan-1989';  
Model.End               = '30-Sep-2009';
Model.PsStart           = '1-Jan-1989';  %p-score estimation sample
Model.PsEnd             = '31-Jul-2005';
Model.HTStart           = '1-Jan-1989';  %response estimation sample 
Model.HTEnd             = '31-Jul-2007';
Model                   = CompMultiImp(Model);
IRFTabPF2               = Create_ImpulseResponse_Table(Model,IRFTabPF2);
SpecTestTab             = CreateSpecTestTable(Model,SpecTestTab,true);



%% NBER Full Sample estimators


Model = SetGenParam;
Model.Type              = 'Macro_OPT1C';
Model.Start             = '1-Jan-1989';  
Model.End               = '31-Dec-2010';
Model.PsStart           = '1-Jan-1989';  %p-score estimation sample
Model.PsEnd             = '31-Dec-2008';
Model.HTStart           = '1-Jan-1989';  %response estimation sample 
Model.HTEnd             = '31-Dec-2010';
Model                   = CompMultiImp(Model);
SpecTestTab             = CreateSpecTestTable(Model,SpecTestTab,false);
SpecTestTabSpx          = CreateSpecTestSpxTable(Model,SpecTestTabSpx,false);



Model = SetGenParam;
Model.MulHTEpar.DemeanDelta   = false;  
Model.Type              = 'Macro_OPT1C';
Model.Start             = '1-Jan-1989';  
Model.End               = '31-Dec-2010';
Model.PsStart           = '1-Jan-1989';  %p-score estimation sample
Model.PsEnd             = '31-Dec-2008';
Model.HTStart           = '1-Jan-1989';  %response estimation sample 
Model.HTEnd             = '31-Dec-2010';
Model.ReportFFED        = true;
Model                   = CompMultiImp(Model);


Model = SetGenParam;
Model.MulHTEpar.DemeanDelta   = false;  
Model.Type              = 'YC_OPT1C';
Model.Start             = '1-Jan-1989';  
Model.End               = '31-Dec-2010';
Model.PsStart           = '1-Jan-1989';  %p-score estimation sample
Model.PsEnd             = '31-Dec-2008';
Model.HTStart           = '1-Jan-1989';  %response estimation sample 
Model.HTEnd             = '31-Dec-2010';
Model                   = CompMultiImp(Model);
SpecTestTab             = CreateSpecTestTable(Model,SpecTestTab,true);



Model = SetGenParam;
Model.Type              = 'Macro_OPT2C';
Model.Start             = '1-Jan-1989';  
Model.End               = '31-Dec-2010';
Model.PsStart           = '1-Jan-1989';  %p-score estimation sample
Model.PsEnd             = '31-Dec-2008';
Model.HTStart           = '1-Jan-1989';  %response estimation sample 
Model.HTEnd             = '31-Dec-2010';
Model                   = CompMultiImp(Model);
SpecTestTab             = CreateSpecTestTable(Model,SpecTestTab,false);
SpecTestTabSpx          = CreateSpecTestSpxTable(Model,SpecTestTabSpx,false);




Model = SetGenParam;
Model.MulHTEpar.DemeanDelta   = false;   
Model.Type              = 'Macro_OPT2C';
Model.Start             = '1-Jan-1989';  
Model.End               = '31-Dec-2010';
Model.PsStart           = '1-Jan-1989';  %p-score estimation sample
Model.PsEnd             = '31-Dec-2008';
Model.HTStart           = '1-Jan-1989';  %response estimation sample 
Model.HTEnd             = '31-Dec-2010';
Model.ReportFFED        = true;
Model                   = CompMultiImp(Model);





Model = SetGenParam;
Model.MulHTEpar.DemeanDelta   = false;   
Model.Type              = 'YC_OPT2C';
Model.Start             = '1-Jan-1989';  
Model.End               = '31-Dec-2010';
Model.PsStart           = '1-Jan-1989';  %p-score estimation sample
Model.PsEnd             = '31-Dec-2008';
Model.HTStart           = '1-Jan-1989';  %response estimation sample 
Model.HTEnd             = '31-Dec-2010';
Model                   = CompMultiImp(Model);
SpecTestTab             = CreateSpecTestTable(Model,SpecTestTab,true);


Model = SetGenParam;
%Model.RepNeg25          = true;     %only report -.25 changes
Model.Type              = 'Macro_OPF1C';
Model.Start             = '1-Jan-1989';  
Model.End               = '31-Dec-2010';
Model.PsStart           = '1-Jan-1989';  %p-score estimation sample
Model.PsEnd             = '31-Dec-2008';
Model.HTStart           = '1-Jan-1989';  %response estimation sample 
Model.HTEnd             = '31-Dec-2010';
Model                   = CompMultiImp(Model);
SpecTestTab             = CreateSpecTestTable(Model,SpecTestTab,false);
SpecTestTabSpx          = CreateSpecTestSpxTable(Model,SpecTestTabSpx,false);


Model = SetGenParam;
Model.MulHTEpar.DemeanDelta   = false;  
%Model.RepNeg25          = true;     %only report -.25 changes
Model.Type              = 'Macro_OPF1C';
Model.Start             = '1-Jan-1989';  
Model.End               = '31-Dec-2010';
Model.PsStart           = '1-Jan-1989';  %p-score estimation sample
Model.PsEnd             = '31-Dec-2008';
Model.HTStart           = '1-Jan-1989';  %response estimation sample 
Model.HTEnd             = '31-Dec-2010';
Model.ReportFFED        = true;
Model                   = CompMultiImp(Model);




Model = SetGenParam;
Model.MulHTEpar.DemeanDelta   = false;  
%Model.RepNeg25          = true;     %only report -.25 changes
Model.Type              = 'YC_OPF1C';
Model.Start             = '1-Jan-1989';  
Model.End               = '31-Dec-2010';
Model.PsStart           = '1-Jan-1989';  %p-score estimation sample
Model.PsEnd             = '31-Dec-2008';
Model.HTStart           = '1-Jan-1989';  %response estimation sample 
Model.HTEnd             = '31-Dec-2010';
Model                   = CompMultiImp(Model);
SpecTestTab             = CreateSpecTestTable(Model,SpecTestTab,true);

%}


Model = SetGenParam;
Model.PlotGraphs        = true;  
Model.RepNeg25         = true;     %only report -.25 changes
Model.Type              = 'Macro_OPF2C';
Model.Start             = '1-Jan-1989';  
Model.End               = '31-Dec-2010';
Model.PsStart           = '1-Jan-1989';  %p-score estimation sample
Model.PsEnd             = '31-Dec-2008';
Model.HTStart           = '1-Jan-1989';  %response estimation sample 
Model.HTEnd             = '31-Dec-2010';
Model                   = CompMultiImp(Model);
IRFTabLongPF2           = Create_ImpulseResponse_Table(Model,[]);
Model                   = PlotFitPredChange(Model);
SpecTestTab             = CreateSpecTestTable(Model,SpecTestTab,false);
SpecTestTabSpx          = CreateSpecTestSpxTable(Model,SpecTestTabSpx,false);



Model = SetGenParam;
Model.PlotGraphs        = true;  
Model.MulHTEpar.DemeanDelta   = false;   
Model.RepNeg25          = true;     %only report -.25 changes
Model.Type              = 'Macro_OPF2C';
Model.Start             = '1-Jan-1989';  
Model.End               = '31-Dec-2010';
Model.PsStart           = '1-Jan-1989';  %p-score estimation sample
Model.PsEnd             = '31-Dec-2008';
Model.HTStart           = '1-Jan-1989';  %response estimation sample 
Model.HTEnd             = '31-Dec-2010';
Model.ReportFFED        = true;
Model                   = CompMultiImp(Model);
IRFTabLongPF2           = Create_ImpulseResponse_Table(Model,IRFTabLongPF2);


Model = SetGenParam;
Model.PlotGraphs        = true;  
Model.MulHTEpar.DemeanDelta   = false;   
Model.RepNeg25          = true;     %only report -.25 changes
Model.Type              = 'YC_OPF2C';
Model.Start             = '1-Jan-1989';  
Model.End               = '31-Dec-2010';
Model.PsStart           = '1-Jan-1989';  %p-score estimation sample
Model.PsEnd             = '31-Dec-2008';
Model.HTStart           = '1-Jan-1989';  %response estimation sample 
Model.HTEnd             = '31-Dec-2010';
Model                   = CompMultiImp(Model);
IRFTabLongPF2           = Create_ImpulseResponse_Table(Model,IRFTabLongPF2);
SpecTestTab             = CreateSpecTestTable(Model,SpecTestTab,true);



%%
%
%Figures 13 - HTE estimators for QE
Model = SetGenParam;
Model.MulHTEpar.DemeanDelta   = false;  
Model.numlev            = 2;
Model.PScore            = 'Probit';
Model.Start             = '1-Jul-2006';  
Model.End               = '31-Dec-2009';
Model.PsStart           = '1-Aug-2006';  %p-score estimation sample
Model.PsEnd             = '31-Dec-2008';
Model.HTStart           = '1-Aug-2006';  %response estimation sample 
Model.HTEnd             = '31-Dec-2009';
Model.Type              = 'Macro_PT';
Model.ImpHorizon        = 12;              % Reduce horizon because of limited data availability
Model                   = CompMultiImp(Model);


Model = SetGenParam;
Model.MulHTEpar.DemeanDelta   = false;  
Model.numlev            = 2;
Model.PScore            = 'Probit';
Model.Start             = '1-Jul-2006';  
Model.End               = '31-Dec-2009';
Model.PsStart           = '1-Aug-2006';  %p-score estimation sample
Model.PsEnd             = '31-Dec-2008';
Model.HTStart           = '1-Aug-2006';  %response estimation sample 
Model.HTEnd             = '31-Dec-2009';
Model.Type              = 'YC_PT';
Model.ImpHorizon        = 12;              % Reduce horizon because of limited data availability
Model                   = CompMultiImp(Model);



%Figures 13 - HTE estimators for QE
Model = SetGenParam;
Model.MulHTEpar.DemeanDelta   = false;  
Model.numlev            = 2;
Model.PScore            = 'Probit';
Model.Start             = '1-Jul-2006';  
Model.End               = '31-Dec-2009';
Model.PsStart           = '1-Aug-2006';  %p-score estimation sample
Model.PsEnd             = '31-Dec-2008';
Model.HTStart           = '1-Aug-2006';  %response estimation sample 
Model.HTEnd             = '31-Dec-2009';
Model.Type              = 'Macro_PF1';
Model.ImpHorizon        = 12;              % Reduce horizon because of limited data availability
Model                   = CompMultiImp(Model);


Model = SetGenParam;
Model.numlev            = 2;
Model.MulHTEpar.DemeanDelta   = false;  
Model.PScore            = 'Probit';
Model.Start             = '1-Jul-2006';  
Model.End               = '31-Dec-2009';
Model.PsStart           = '1-Aug-2006';  %p-score estimation sample
Model.PsEnd             = '31-Dec-2008';
Model.HTStart           = '1-Aug-2006';  %response estimation sample 
Model.HTEnd             = '31-Dec-2009';
Model.Type              = 'Macro_PF1';
Model.ImpHorizon        = 12;              % Reduce horizon because of limited data availability
Model.ReportFFED        = true;
Model                   = CompMultiImp(Model);




Model = SetGenParam;
Model.numlev            = 2;
Model.MulHTEpar.DemeanDelta   = false;  
Model.PScore            = 'Probit';
Model.Start             = '1-Jul-2006';  
Model.End               = '31-Dec-2009';
Model.PsStart           = '1-Aug-2006';  %p-score estimation sample
Model.PsEnd             = '31-Dec-2008';
Model.HTStart           = '1-Aug-2006';  %response estimation sample 
Model.HTEnd             = '31-Dec-2009';
Model.Type              = 'YC_PF1';
Model.ImpHorizon        = 12;              % Reduce horizon because of limited data availability
Model                   = CompMultiImp(Model);

Model = SetGenParam;
Model.MulHTEpar.DemeanDelta   = false;  
Model.PlotGraphs        = true;  
Model.numlev            = 2;
Model.PScore            = 'Probit';
Model.Start             = '1-Jul-2006';  
Model.End               = '31-Dec-2009';
Model.PsStart           = '1-Aug-2006';  %p-score estimation sample
Model.PsEnd             = '31-Dec-2008';
Model.HTStart           = '1-Aug-2006';  %response estimation sample 
Model.HTEnd             = '31-Dec-2009';
Model.Type              = 'Macro_PF2';
Model.ImpHorizon        = 12;              % Reduce horizon because of limited data availability
Model                   = CompMultiImp(Model);



Model = SetGenParam;
Model.PlotGraphs        = true;  
Model.numlev            = 2;
Model.MulHTEpar.DemeanDelta   = false;  
Model.PScore            = 'Probit';
Model.Start             = '1-Jul-2006';  
Model.End               = '31-Dec-2009';
Model.PsStart           = '1-Aug-2006';  %p-score estimation sample
Model.PsEnd             = '31-Dec-2008';
Model.HTStart           = '1-Aug-2006';  %response estimation sample 
Model.HTEnd             = '31-Dec-2009';
Model.Type              = 'Macro_PF2';
Model.ImpHorizon        = 12;              % Reduce horizon because of limited data availability
Model.ReportFFED        = true;
Model                   = CompMultiImp(Model);


Model = SetGenParam;
Model.PlotGraphs        = true;  
Model.numlev            = 2;
Model.MulHTEpar.DemeanDelta   = false;  
Model.PScore            = 'Probit';
Model.Start             = '1-Jul-2006';  
Model.End               = '31-Dec-2009';
Model.PsStart           = '1-Aug-2006';  %p-score estimation sample
Model.PsEnd             = '31-Dec-2008';
Model.HTStart           = '1-Aug-2006';  %response estimation sample 
Model.HTEnd             = '31-Dec-2009';
Model.Type              = 'YC_PF2';
Model.ImpHorizon        = 12;              % Reduce horizon because of limited data availability
Model                   = CompMultiImp(Model);


Model = SetGenParam;
Model.MulHTEpar.DemeanDelta   = false;  
Model.numlev            = 2;
Model.PScore            = 'Probit';
Model.Start             = '1-Jul-2006';  
Model.End               = '31-Dec-2009';
Model.PsStart           = '1-Aug-2006';  %p-score estimation sample
Model.PsEnd             = '31-Dec-2008';
Model.HTStart           = '1-Aug-2006';  %response estimation sample 
Model.HTEnd             = '31-Dec-2009';
Model.Type              = 'Macro_PF3';
Model.ImpHorizon        = 12;              % Reduce horizon because of limited data availability
Model                   = CompMultiImp(Model);


Model = SetGenParam;
Model.numlev            = 2;
Model.MulHTEpar.DemeanDelta   = false;  
Model.PScore            = 'Probit';
Model.Start             = '1-Jul-2006';  
Model.End               = '31-Dec-2009';
Model.PsStart           = '1-Aug-2006';  %p-score estimation sample
Model.PsEnd             = '31-Dec-2008';
Model.HTStart           = '1-Aug-2006';  %response estimation sample 
Model.HTEnd             = '31-Dec-2009';
Model.Type              = 'Macro_PF3';
Model.ImpHorizon        = 12;              % Reduce horizon because of limited data availability
Model.ReportFFED        = true;
Model                   = CompMultiImp(Model);


Model = SetGenParam;
Model.numlev            = 2;
Model.MulHTEpar.DemeanDelta   = false;  
Model.PScore            = 'Probit';
Model.Start             = '1-Jul-2006';  
Model.End               = '31-Dec-2009';
Model.PsStart           = '1-Aug-2006';  %p-score estimation sample
Model.PsEnd             = '31-Dec-2008';
Model.HTStart           = '1-Aug-2006';  %response estimation sample 
Model.HTEnd             = '31-Dec-2009';
Model.Type              = 'YC_PF3';
Model.ImpHorizon        = 12;              % Reduce horizon because of limited data availability
Model                   = CompMultiImp(Model);


%}
close('all');         % close all figure windows
%%

SpecTestTab             = PrintSpecTestTable(SpecTestTab,'SpecTestResultsFFT.tex');
SpecTestTabSpx          = PrintSpecTestTable(SpecTestTabSpx,'SpecTestSpxResultsFFT.tex');

IRFTabPF2               = PrintImpRespTable(IRFTabPF2,'IRFTabPF2.tex',6,6,true);
IRFTabLongPF2           = PrintImpRespTable(IRFTabLongPF2,'IRFTabLongPF2.tex',6,6,true);


