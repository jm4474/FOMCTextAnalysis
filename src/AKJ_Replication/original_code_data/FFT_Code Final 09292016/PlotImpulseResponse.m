function R = PlotImpulseResponse(R,varargin)
% =========================================================================
% PlotImpulseResponse
% -------------------
% Plot impulse-response functions estimated via DynamicHTE
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
% CI            : Length of confidence interval ("1sd" (default) | "2sd" | user-specified numeric value)
% Policy        : Choice of policies to be included in the figure ("all" (default) | user-specified numeric array)
% BWDisplay     : Print figure in black and white ("off" (default) | "on")
% Orientation   : Either to place policies in columns ("Portrait") or variables ("Landscape") ("Portrait" (default) | "Landscape")
% Columns       : Number of columns in a single page, must be a numeric value, default = 2
% Visible       : Hide pop-up window ("off" (default) | "on")
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
defaultCI = '1sd';
addParamValue(p,'CI',defaultCI);
defaultPolicy = 'all';
addParamValue(p,'Policy',defaultPolicy);
defaultBWDisplay = 'off';
addParamValue(p,'BWDisplay',defaultBWDisplay,@ischar);
defaultOrientation = 'Portrait';
addParamValue(p,'Orientation',defaultOrientation,@ischar);
defaultTitles = {};
addParamValue(p,'Titles',defaultTitles,@iscellstr);
defaultColumns = 2;
addParamValue(p,'Columns',defaultColumns,@isnumeric);
defaultVisible = 'off';
addParamValue(p,'Visible',defaultVisible,@ischar);
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
        error('PlotImpulseResponse::Unidentified input parameter: Outcomes');
    end
elseif isnumeric(p.Results.Outcomes)
    if length(p.Results.Outcomes) <= ky
        PickVarInd = p.Results.Outcomes;
        VarNames = R.Inp.OutcomeVarN(PickVarInd);
        NumVarPick = length(p.Results.Outcomes);
    else
        error('PlotImpulseResponse::Index exceeds total number of outcome variables');
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
            error('PlotImpulseResponse::Outcome variable names does not match with the data');
        elseif length(ActualPickVarInd) < NumVarPick
            fprintf('\n');
            fprintf('PlotImpulseResponse::Some names does not match with the data. Keeping existing ones only... \n');
            PickVarInd = ActualPickVarInd;
            VarNames = R.Inp.OutcomeVarN(PickVarInd);
            NumVarPick = length(PickVarInd);
        else
        end
    else
        error('PlotImpulseResponse::Index exceeds total number of outcome variables');
    end
else
    error('PlotImpulseResponse::Current version does not support this option: Outcomes');
end

% Get impulse-response functions
if strcmpi(p.Results.ResponseType,'Level')
    IR = R.Out.result.g(PickVarInd);
    IRs = R.Out.result.gs(PickVarInd);
elseif strcmpi(p.Results.ResponseType,'Cumulative')
    IR = R.Out.result.gc(PickVarInd);
    IRs = R.Out.result.gcs(PickVarInd);
else
    error('PlotImpulseResponse::Unidentified input parameter: ResponseType');
end

% Size of confidence interval
if isnumeric(p.Results.CI)
    alpha = 1-p.Results.CI;
    if alpha <= 0 || alpha >= 1
        error('PlotImpulseResponse::Cannot draw confidence interval, size should be 0<alpha<1');
    else
        coef = norminv(1-alpha/2,0,1);
    end
elseif ischar(p.Results.CI)
    if strcmpi(p.Results.CI,'1sd')
        coef = 1;
    elseif strcmpi(p.Results.CI,'2sd')
        coef = 2;
    else
        error('PlotImpulseResponse::Unidentified input parameter: Interval');
    end
else
    error('PlotImpulseResponse::Unidentified input parameter: Interval');
end

% Choice of policy shock
if ischar(p.Results.Policy)
    if strcmpi(p.Results.Policy,'all')
        PolicyPick = Pol;
        NumPolicyPick = length(PolicyPick);
        ImpulseLoc = (1:NumPolicyPick);
    else
        error('PlotImpulseResponse::Unidentified input parameter: Policy');
    end
elseif isnumeric(p.Results.Policy)
    PolicyPick = p.Results.Policy;
    NumPolicyPick = length(PolicyPick);
    ImpulseLoc = zeros(1,NumPolicyPick);
    for j = 1:NumPolicyPick
        if any(Pol==PolicyPick(j))
            ImpulseLoc(j) = find(Pol==PolicyPick(j));
        else
            error('PlotImpulseResponse::Some of the specified policies does not match with the input data');
        end
    end
else
    error('PlotImpulseResponse::Unidentified input parameters: Policy');
end

% Turn on/off black-and-white display
if strcmpi(p.Results.BWDisplay,'off')
    LinSpecIRF = {'-b' '--r'};
elseif strcmpi(p.Results.BWDisplay,'on')
    LinSpecIRF = {'-k' '--k'};
else
    error('PlotImpulseResponse::Unidentified input parameter: BWDisplay');
end

% Choose display orientation and number of pages
if strcmpi(p.Results.Orientation,'Portrait')
    DispLandscape = 0;
    ColPerPage = min(round(p.Results.Columns),NumPolicyPick);
    RowPerPage = NumVarPick;
    NumPages = ceil(NumPolicyPick/ColPerPage);
    TotalNumCols = NumPolicyPick;
elseif strcmpi(p.Results.Orientation,'Landscape')
    DispLandscape = 1;
    ColPerPage = min(round(p.Results.Columns),NumVarPick);
    RowPerPage = NumPolicyPick;
    NumPages = ceil(NumVarPick/ColPerPage);
    TotalNumCols = NumVarPick;
else
    error('PlotImpulseResponse::Unidentified input parameter: Orientation');
end

% Assign column headers
if isempty(p.Results.Titles)
    TitleNames = VarNames;
else
    if length(p.Results.Titles) ~= NumVarPick
        error('TabImpulseResponse::User-specified column headers are unmatched with number of variables');
    else
        TitleNames = p.Results.Titles;
    end
end

% Get file name
ToggleVisibility = p.Results.Visible;
NamePrefix = p.Results.FileName;

%% Plot IRF
TimeLine = (1:hz)';

for pp = 1:NumPages
    
    % set function control
    fh = figure('Visible',ToggleVisibility);
    
    % pick (sub-)index to include
    InThisPage = (ColPerPage*(pp-1)+1:min(ColPerPage*pp,TotalNumCols));
    ColThisPage = length(InThisPage);
    
    % iterate panels for each row
    for rr = 1:RowPerPage
        
        % pick subset of estimates to be displaced in the same row
        if DispLandscape == 1
            % landscape mode: pick same policy for different variables
            PickIRF = zeros(hz,ColThisPage);
            PickIRFse = zeros(hz,ColThisPage);
            for ii = 1:ColThisPage
                PickIRF(:,ii) = IR{InThisPage(ii)}(:,ImpulseLoc(rr));
                PickIRFse(:,ii) = IRs{InThisPage(ii)}(:,ImpulseLoc(rr));
            end
        else
            % portrait mode: pick same variable for different policies
            PickIRF = IR{rr}(:,ImpulseLoc(InThisPage));
            PickIRFse = IRs{rr}(:,ImpulseLoc(InThisPage));
        end
        
        % set bounds for vertical axis
        IRFmax = max(max(PickIRF+coef*PickIRFse));
        IRFmin = min(min(PickIRF-coef*PickIRFse));
        
        % iterate panels for each column
        for cc = 1:ColThisPage
            subplot(RowPerPage,ColThisPage,ColThisPage*(rr-1)+cc)
            grid on;
            hold on;
            plot(TimeLine,zeros(hz,1),'-k');
            plot(TimeLine,PickIRF(:,cc),LinSpecIRF{1},'LineWidth',1.5);
            plot(TimeLine,PickIRF(:,cc)+coef*PickIRFse(:,cc),LinSpecIRF{2},'LineWidth',1.5);
            plot(TimeLine,PickIRF(:,cc)-coef*PickIRFse(:,cc),LinSpecIRF{2},'LineWidth',1.5);
            hold off;
            
            % print title for each panel
            if DispLandscape == 1
                title([num2str(Pol(ImpulseLoc(rr))) ' effect on ' TitleNames{InThisPage(cc)}]);
            else
                title([num2str(Pol(ImpulseLoc(InThisPage(cc)))) ' effect on ' TitleNames{rr}]);
            end
            
            % customize axis
            set(gca,'YLim',[IRFmin*1.15 IRFmax*1.15]);
            set(gca,'XLim',[1 hz]);
            set(gca,'XTick',(4:4:hz));
        end
    end
    
    % fit printed area to minimize unwanted blank area
    ScrSize = get(fh,'PaperSize');
    set(fh,'PaperSize',[ScrSize(1)*(ColThisPage/2) ScrSize(2)*(RowPerPage/4)]);
    set(fh,'PaperPosition',[0 0 ScrSize(1)*(ColThisPage/2) ScrSize(2)*(RowPerPage/4)]);
    set(fh,'PaperPositionMode','manual');
    
    % save figures into pdf format
    if NumPages == 1
        saveas(fh,strcat(NamePrefix,'_fig_IRF'),'pdf');
    else
        saveas(fh,strcat(NamePrefix,'_fig_IRF',num2str(pp)),'pdf');
    end
end

%% End of program
fprintf('\n');
fprintf('Impulse-response functions saved in %1s',strcat(NamePrefix,'_fig_IRF.pdf'));
fprintf('\n');

end