function Model = CompMultiImp(Model)

%This routine populates the structure 'Model' with information about data
%input files, covariates for the propensity model and outcome variables for
%the impulses. Additional control variables such as the number of impulse
%coefficients are assigned as well. The corresponding ModelDefinitions.m
%file can be modified to change the output of the code. 
Model = ModelDefinitions(Model); 

%Based on the input in the previous module, this module loads datasets and
%transforms them into a format that can be used as input for subsequent
%computations. All data are stored as fields within the 'Model' structure.
Model = LoadData(Model);


%This module carries out the statistical analysis by estimating the
%propensity score and computing the impulse response functions. 
switch Model.ImpType 
    case {'NL'}
        Model = NonLinImp_CntLagOutc(Model); 
 end

switch Model.PScore
  case{'Oprob'}
      
      Model.SpecTestPrintNames = Model.OutcomePrintNames;
      
      si = strcmp(Model.OutcomePrintNames,'Federal Funds Rate');
      if ~isempty(strfind(Model.Type,'YC')) && ~isempty(find(si))
          Model.SpecTestPrintNames = Model.OutcomePrintNames(~si);
          Model.SpecTestPrintNames = [Model.SpecTestPrintNames;'Funds Rate (End of Month)'];
      end
      
      
      Model = SpecTestsDelta(Model);
 
      % Tests for combined yields
      
      Model.CombineTestVar = Model.CombineTestVarYields; %load combination variables
      Model = SpecTestsCombinedDelta(Model);

      Model.SpecTestVarN       = [cellstr('Combined Yields');Model.SpecTestVarN];
      Model.SpecTestPrintNames = [cellstr('Combined Yields');Model.SpecTestPrintNames];         
      Model.SpecTest           = [Model.SpecTestCombined;Model.SpecTest];
      Model.SpecTestStat       = [Model.SpecTestCombinedStat;Model.SpecTestStat];
      

     % Tests for all combined outcome Variables
      if ~strcmp(Model.RespType,'YC');
          Model.CombineTestVar = Model.CombineTestAllOutcomes; %load combination variables
          Model.Diag.yMspecT   = Model.Diag.Ytest;             %move combined variables in test 
          Model = SpecTestsCombinedAllDelta(Model);     

          Model.SpecTestVarN       = [cellstr('All Outcomes');Model.SpecTestVarN];
          Model.SpecTestPrintNames = [cellstr('All Outcomes');Model.SpecTestPrintNames];         
          Model.SpecTest           = [Model.SpecTestCombined;Model.SpecTest];
          Model.SpecTestStat       = [Model.SpecTestCombinedStat;Model.SpecTestStat];
      end
      
      
      Model = SpecTestsPscoreVarDelta(Model);
      
      Model.CombineTestVar = Model.CombineTestVarSpx; %load combination variables
      Model = SpecTestsPscoreVarCombinedDelta(Model);
      % merge combined test results with Pscore test results
      Model.SpecTestSpxVarN     = [cellstr('Combined');Model.SpecTestSpxVarN];
      Model.SpecTestPscore      = [Model.SpecTestPscoreCombined;Model.SpecTestPscore];
      Model.SpecTestPscoreStat  = [Model.SpecTestPscoreCombinedStat;Model.SpecTestPscoreStat];
    case {'Probit','Multinom'}
      Model.SpecTestPrintNames = Model.OutcomePrintNames;        
      si = strcmp(Model.OutcomePrintNames,'Federal Funds Rate');
      if ~isempty(strfind(Model.Type,'YC')) && ~isempty(find(si))
          Model.SpecTestPrintNames = Model.OutcomePrintNames(~si);
      end

end

if Model.PlotGraphs
   Model = PlotResults(Model);
end

close('all');         % close all figure windows

return;