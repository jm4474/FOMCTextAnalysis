function R = TabImpulseResponse(R,varargin)
% =========================================================================
% TabImpulseResponse
% ------------------
% Tabulate impulse-response functions estimated via DynamicHTE
%
% date : 9/22/2016
% author : Sungho Noh
%
% -----------------
% REQUIRED INPUT(s)
% -----------------
% R : Output data saved in structure format produced by DynamicHTE
%
% -----------------
% OPTIONAL INPUT(s)
% -----------------
% Outcomes      : Choice of outcome variables to be included in the figure ("all" (default) | user-specified numeric or string array)
% ResponseType  : Choose either levels or cumulative response ("Level" (default) | "Cumulative")
% Policy        : Choice of policies to be included in the figure ("all" (default) | user-specified numeric array)
% Interval      : Pick a subset of estimates, either scalar or numeric vector, must be less than the total number of estimates (=R.Inp.hz) (default = 4, implying a quarter if underlying process is Monthly)
% Columns       : Number of columns in a table, must be a numeric value, (default is to include every outcomes chosen in a single table)
% Align         : Align numbers within a column ("c" or "Center" (default) | "r" or "Right" | "l" or "Left")
% Headers       : User-specified column headers for each outcome variable, must be a cell string with size equal to the number of variables chosen
% Booktabs      : Use booktabs package ("off" (default) | "on")
% FileName      : Set prefix of filenames, default is "DynamicHTE"
%
% =========================================================================
p = inputParser;

%% Required input(s)
addRequired(p,'R');

%% Retrieve information from required input(s)
Pol = R.Inp.Policy;
zp = R.Inp.zp;
Pol(Pol==zp) = [];
VarNamesAll = R.Inp.OutcomeVarN;
ky = length(VarNamesAll);
hz = R.Cont.HTEpar.Horizon;

%% Optional settings
defaultOutcomes = 'all';
addParamValue(p,'Outcomes',defaultOutcomes);
defaultResponseType = 'Level';
addParamValue(p,'ResponseType',defaultResponseType,@ischar);
defaultPolicy = 'all';
addParamValue(p,'Policy',defaultPolicy);
defaultInterval = 4;
addParamValue(p,'Interval',defaultInterval,@isnumeric);
defaultColumns = ky;
addParamValue(p,'Columns',defaultColumns,@isnumeric);
defaultAlign = 'c';
addParamValue(p,'Align',defaultAlign,@ischar);
defaultHeaders = {};
addParamValue(p,'Headers',defaultHeaders,@iscellstr);
defaultBooktabs = 'off';
addParamValue(p,'Booktabs',defaultBooktabs,@ischar);
defaultFileName = 'DynamicHTE';
addParamValue(p,'FileName',defaultFileName,@ischar);

%% Arrange input arguments
parse(p,R,varargin{:});

%% Set parameters
% Pick outcome variables
if ischar(p.Results.Outcomes)
    if strcmpi(p.Results.Outcomes,'all')
        VarNames = VarNamesAll;
        PickVarInd = (1:ky);
        NumVarPick = ky;
    elseif sum(strcmpi(p.Results.Outcomes,VarNamesAll))
        VarNames = VarNamesAll(strcmpi(p.Results.Outcomes,VarNamesAll));
        VarInd = (1:ky);
        PickVarInd = VarInd(strcmpi(p.Results.Outcomes,VarNamesAll));
        NumVarPick = 1;
    else
        error('TabImpulseResponse::Unidentified input parameter: Outcomes');
    end
elseif isnumeric(p.Results.Outcomes)
    if length(p.Results.Outcomes) <= ky
        PickVarInd = p.Results.Outcomes;
        VarNames = R.Inp.OutcomeVarN(PickVarInd);
        NumVarPick = length(p.Results.Outcomes);
    else
        error('TabImpulseResponse::Index exceeds total number of outcome variables');
    end
elseif iscellstr(p.Results.Outcomes)
    VarNames = p.Results.Outcomes;
    NumVarPick = length(VarNames);
    PickVarInd = zeros(1,NumVarPick);
    if NumVarPick <= ky
        for i = 1:NumVarPick
            for j = 1:ky
                if strcmpi(VarNames{i},VarNamesAll{j})
                    PickVarInd(1,i) = j;
                else
                end
            end
        end
        PickVarInd(PickVarInd==0) = [];
        ActualPickVarInd = unique(PickVarInd);
        if isempty(ActualPickVarInd)
            error('TabImpulseResponse::Outcome variable names does not match with the data');
        elseif length(ActualPickVarInd) < NumVarPick
            fprintf('\n');
            fprintf('TabImpulseResponse::Some names does not match with the data. Keeping existing ones only... \n');
            PickVarInd = ActualPickVarInd;
            VarNames = R.Inp.OutcomeVarN(PickVarInd);
            NumVarPick = length(PickVarInd);
        else
        end
    else
        error('TabImpulseResponse::Index exceeds total number of outcome variables');
    end
else
    error('TabImpulseResponse::Current version does not support this option: Outcomes');
end

% Get impulse-response functions
if strcmpi(p.Results.ResponseType,'Level')
    IR = R.Out.result.g(PickVarInd);
    IRs = R.Out.result.gs(PickVarInd);
    IRp = R.Out.result.p(PickVarInd);
elseif strcmpi(p.Results.ResponseType,'Cumulative')
    IR = R.Out.result.gc(PickVarInd);
    IRs = R.Out.result.gcs(PickVarInd);
    IRp = R.Out.result.pc(PickVarInd);
else
    error('TabImpulseResponse::Unidentified input parameter: ResponseType');
end

% Choice of policy shock
if ischar(p.Results.Policy)
    if strcmpi(p.Results.Policy,'all')
        PolicyPick = Pol;
        NumPolicyPick = length(PolicyPick);
        ImpulseLoc = (1:NumPolicyPick);
    else
        error('TabImpulseResponse::Unidentified input parameter: Policy');
    end
elseif isnumeric(p.Results.Policy)
    PolicyPick = p.Results.Policy;
    NumPolicyPick = length(PolicyPick);
    ImpulseLoc = zeros(1,NumPolicyPick);
    for j = 1:NumPolicyPick
        if any(Pol==PolicyPick(j))
            ImpulseLoc(j) = find(Pol==PolicyPick(j));
        else
            error('TabImpulseResponse::Some of the specified policies does not match with the input data');
        end
    end
else
    error('TabImpulseResponse::Unidentified input parameter: Policy');
end

% Estimates to be included in table
if max(p.Results.Interval) >= hz
    error('TabImpulseResponse::Interval exceeds total number of estimates');
elseif length(p.Results.Interval) == 1
    intv = round(p.Results.Interval);
    PickPeriod = (1:hz/intv)*intv;
    NumPeriods = length(PickPeriod);
else
    PickPeriod = p.Results.Interval;
    NumPeriods = length(PickPeriod);
end

% Number of columns in a single table
VarPerTab = round(p.Results.Columns);
NumTable = ceil(NumVarPick/VarPerTab);

% Numbers aligned in column
if strcmpi(p.Results.Align,'c') || strcmpi(p.Results.Align,'Center')
    ColAlign = 'c';
elseif strcmpi(p.Results.Align,'r') || strcmpi(p.Results.Align,'Right')
    ColAlign = 'r';
elseif strcmpi(p.Results.Align,'l') || strcmpi(p.Results.Align,'Left')
    ColAlign = 'l';
else
    error('TabImpulseResponse::Unidentified input parameter: Align');
end

% Assign column headers
if isempty(p.Results.Headers)
    ColumnHeaders = VarNames;
else
    if length(p.Results.Headers) ~= NumVarPick
        error('TabImpulseResponse::User-specified column headers are unmatched with number of variables');
    else
        ColumnHeaders = p.Results.Headers;
    end
end

% Use Booktabs package
if strcmpi(p.Results.Booktabs,'on')
    UseBooktabs = 1;
elseif strcmpi(p.Results.Booktabs,'off')
    UseBooktabs = 0;
else
    error('TabImpulseResponse::Unidentified input parameter: Booktabs');
end

% Get file name
NamePrefix = p.Results.FileName;

% Number of stars
StarThres = [.001 .05 .1];
StarNum = cell(size(IRp));
for kk = 1:NumVarPick
    StarNum_k = zeros(hz,R.Inp.NumPolicy);
    for hh = 1:hz
        for pp = 1:R.Inp.NumPolicy-1
            StarNum_k(hh,pp) = sum((IRp{kk}(hh,pp) <= StarThres));
        end
    end
    StarNum{kk} = StarNum_k;
end

%% Write table in TeX format
fclose('all');
fid = fopen(strcat(NamePrefix,'_tab_IRF.tex'),'w');

% Preamble
fprintf(fid,'\\documentclass{article}\n');
if UseBooktabs
    fprintf(fid,'\\usepackage{booktabs}\n\n');
else
    fprintf(fid,'\n');
end
fprintf(fid,'\\begin{document}\n\n');

% Iterate for the number of tables
for tnum = 1:NumTable
    
    % Index of variables to be included in current table
    InThisTab = (VarPerTab*(tnum-1)+1:min(VarPerTab*tnum,NumVarPick));
    VarThisTab = length(InThisTab);
    
    % Begin table
    fprintf(fid,'\\begin{table}\n');
    fprintf(fid,'\\centering\n');
    
    % Begin tabular environment
    fprintf(fid,'\\begin{tabular}{r');
    for cnum = 1:NumPolicyPick*VarThisTab
        fprintf(fid,'%1s',ColAlign);
    end
    fprintf(fid,'}\n');
    
    % Add horizontal line (top)
    if UseBooktabs
        fprintf(fid,'\\toprule\n');
    else
        fprintf(fid,'\\hline\\hline\n');
    end
    
    % Column header (1): Variable names
    fprintf(fid,'%6s','');
    for vnum = 1:VarThisTab
        fprintf(fid,'\t& \\multicolumn{%1.0f}{c}{\\textbf{%1s}}',NumPolicyPick,ColumnHeaders{InThisTab(vnum)});
    end
    fprintf(fid,'\\\\\n');
    
    if UseBooktabs
        fprintf(fid,'\\cmidrule{%1.0f-%1.0f}\n',[2 NumPolicyPick*VarThisTab+1]);
    else
        fprintf(fid,'\\cline{%1.0f-%1.0f}\n',[2 NumPolicyPick*VarThisTab+1]);
    end
    
    % Column header (2): Policy choices
    fprintf(fid,'%6s', '');
    for vnum = 1:VarThisTab
        for pnum = 1:NumPolicyPick
            fprintf(fid,'\t& $%10.2f$',PolicyPick(pnum));
        end
    end
    fprintf(fid,' \\\\\n');
    
    % Add horizontal line (separate estimates from headers)
    if UseBooktabs
        fprintf(fid,'\\midrule\n');
    else
        fprintf(fid,'\\hline\n');
    end
    
    % Enter estimates by each period
    for rnum = 1:NumPeriods
        
        % Point estimates in first row
        fprintf(fid,'$%4.0f$',PickPeriod(rnum));
        for vnum = 1:VarThisTab
            for pnum = 1:NumPolicyPick
                fprintf(fid,'\t& $%8.3f$',IR{InThisTab(vnum)}(PickPeriod(rnum),ImpulseLoc(pnum)));
                NumStarAdded = StarNum{InThisTab(vnum)}(PickPeriod(rnum),ImpulseLoc(pnum));
                for ss = 1:NumStarAdded
                    fprintf(fid,'*'); % put stars beside the estimate
                end
            end
        end
        fprintf(fid,' \\\\\n');
        
        % Standard errors in second row (in parenthesis)
        fprintf(fid,'%6s','');
        for vnum = 1:VarThisTab
            for pnum = 1:NumPolicyPick
                fprintf(fid,'\t& ($%6.3f$)',IRs{InThisTab(vnum)}(PickPeriod(rnum),ImpulseLoc(pnum)));
            end
        end
        fprintf(fid,' \\\\\n');
        
    end
    
    % Add horizontal line (bottom)
    if UseBooktabs
        fprintf(fid,'\\bottomrule\n');
    else
        fprintf(fid,'\\hline\\hline\n');
    end
    
    % End table
    fprintf(fid,'\\end{tabular}\n');
    fprintf(fid,'\\end{table}\n');
    fprintf(fid,'\n\n');

end

% End document
fprintf(fid,'\n');
fprintf(fid,'\\end{document}\n');

% Close TeX file
fclose(fid);

%% End of program
fprintf('\n');
fprintf('Estimates printed in %1s',strcat(NamePrefix,'_tab_IRF.tex'));
fprintf('\n');

end

