function Model=PlotResults(Model)

respType   = Model.RespType;
crit       = Model.ImpRespCrit;
hor        = Model.ImpHorizon;
if isfield(Model,'Diag')
    if isfield(Model.Diag,'effnumlev')
        numlev = Model.Diag.effnumlev;
        levInd = Model.Diag.levInd;
        if Model.MultiNomQE
           levInd = levInd(1:end-1,:);
           numlev = numlev-1;
        end    
        level  = Model.level;
        level  = fliplr(level(levInd,:)')';
    else
        numlev     = Model.numlev;  
        level      = fliplr(Model.level')'; % report rate increses first
    end
else
     numlev     = Model.numlev;  
     level      = fliplr(Model.level')'; % report rate increses first
end


switch Model.RespType
    case {'YC'}
        figPerPlot = 2*ones(size(Model.DoReportList,1),1)'*Model.DoReportList;
    case {'MacroVAR'}
        figPerPlot =  2*ones(size(Model.DoReportList,1),1)'*Model.DoReportList;
end

if numlev == 5 && Model.Rep25 && ~Model.RepNeg25
    if Model.LinRes
%        level = level(2:3,1); 
       level = level(2:end-1,1);      % comment out this line if only one direction 
    else
        level = level(2:end-1,1);      
    end
elseif Model.RepQE
    level      = [level;0 ];
elseif numlev==2 && strcmp(Model.RespType,'YC')
    figPerPlot =  2*ones(size(Model.DoReportList,1),1)'*Model.DoReportList;    
elseif Model.LinRes
elseif Model.RepNeg25
    level = level((numlev-1)/2+1:end-1,1); % only report one direction of response 
    numlev= 2;
    figPerPlot =  ones(size(Model.DoReportList,1),1)'*Model.DoReportList;    
end


if strcmp('Probit',Model.PScore);
    %Model.LinRes || strcmp('Probit',Model.PScore);
   figPerPlot =  ones(size(Model.DoReportList,1),1)'*Model.DoReportList;
end


numresp    = size(Model.yM,2);
j          = 1;
h(j)       = figure('Visible','off'); % open first graphics window
pli   = 0;
tabNo = 1;

if Model.SlideMode
    figPerPlot    = min(figPerPlot,4);
    Model.PrintOr = 'Landscape';
end

[mins,maxs] = FindPlotYMinMax(Model);


for i = 1:numresp
    if Model.DoReportList(i) % variable is marked for reporting on Impulse Graphs (see SetDoNotPrintList.m)
        if strcmp(Model.PlotType,'Cumulative') || strcmp(Model.PlotType,'DoubleCum');
           Gamma    = fliplr(Model.result(i).gc);
           GammaSTD = fliplr(Model.result(i).gcs);
        elseif strcmp(Model.PlotType,'Individual');
           Gamma    = fliplr(Model.result(i).g);
           GammaSTD = fliplr(Model.result(i).gs);
        else
            error('Unsupported PlotType');
        end

        switch respType
            case 'Macro'
                %rescale response to Percent
                Gamma = 100*Gamma;
                GammaSTD = 100*GammaSTD;
            case 'MacroVAR'
                %rescale response to Percent
                if (strcmp(Model.OutcomeVarN(i),Model.VARLogTransList)'*ones(size(Model.VARLogTransList,1),1))==1 % transform Log vars to % changes
                    Gamma = 100*Gamma;
                    GammaSTD = 100*GammaSTD;            
                end
        end
        if Model.SlideMode
            if figPerPlot == 1 
                le = 1;
                wi = 1;
            else
                wi = 2;
                le = ceil(figPerPlot/wi);
            end
        else            
            if figPerPlot>3
                le = ceil(figPerPlot/2);
                wi = ceil(figPerPlot/le);
            elseif figPerPlot == 3
                le = 3;
                wi = ceil(figPerPlot/le);            
            elseif figPerPlot == 2
                le = 2;
                wi = ceil(figPerPlot/le);
            else
                le = 1;
                wi = ceil(figPerPlot/le);
            end        
        end
        ii = 1;
        while ii <= length(level)-1;      
            pli=pli+1;

            if mod(pli,figPerPlot) > 0   
                    subplot(le,wi,mod(pli,figPerPlot));
            else
                    subplot(le,wi,figPerPlot);
            end  

            % handle case where only reporting +/- .25% separately
            if numlev == 5 && Model.Rep25 && ~Model.RepQE && ~Model.RepNeg25
                %numlev == 5 && Model.Rep25 && ~Model.LinRes && ~Model.RepQE
                jj = ii + 1;
            elseif Model.RepQE
                jj = 1;
                ii = length(level);
            elseif numlev == 2 && Model.RepNeg25
                Gamma = Gamma(:,3);
                GammaSTD = GammaSTD(:,3);
                jj = 1;
                ii = length(level);
                
            else
                jj = ii;
            end


            h=plot((1:hor)',Gamma(:,jj),'-r','LineWidth',1);
    %        if ~Model.LinRes  % only plot standard errors for unrestricted impulses, becasue not yet programmed
                hold on
                if ~Model.VARReportVARImp
                    plot((1:hor)',(Gamma(:,jj)-crit*GammaSTD(:,jj)),'--r','LineWidth',1)
                    plot((1:hor)',(Gamma(:,jj)+crit*GammaSTD(:,jj)),'--r','LineWidth',1)
                    if Model.Plot1StdE
                        plot((1:hor)',(Gamma(:,jj)-GammaSTD(:,jj)),'.r','LineWidth',1)
                        plot((1:hor)',(Gamma(:,jj)+GammaSTD(:,jj)),'.r','LineWidth',1)
                    end
                %    plot((1:hor)',(Gamma(:,jj)-1*GammaSTD(:,jj)),'.r','LineWidth',1)
                %    plot((1:hor)',(Gamma(:,jj)+1*GammaSTD(:,jj)),'.r','LineWidth',1)
  
                    plotvals   = Gamma;
                    plotvalsdn = Gamma-crit*GammaSTD;
                    plotvalsup = Gamma+crit*GammaSTD;
                else
                    plot((1:hor)',(GammaSTD(:,jj)),'--r','LineWidth',1)
                    plot((1:hor)',(GammaSTD(:,jj+1)),'--r','LineWidth',1)
                    plotvals = GammaSTD(:,jj);
                    plotvals = [plotvals,GammaSTD(:,jj+1)];

                end                
                hold off
     %       end
            if numlev == 5 && Model.Rep25 
                 if ii+1<Model.zp
                        id = ii;
                    else
                        id = ii+1;
                 end            
            else
                if ii<Model.zp
                    id = ii;
                else
                    id = ii+1;
                end
            end
            if Model.PlotSameY
                minv = min(mins);
                maxv = max(maxs);
            else                
                minv = mins(i,1);
                maxv = maxs(i,1);
            end
            set(gca,'YLIM',[minv,maxv]);
            
            grid on
            set(h,'Color','red','LineWidth',2.22)
 
            if hor<=12
                set(gca,'XTick',(2:2:hor));
            else
                set(gca,'XTick',(3:3:hor));                
            end
            set(gca,'XLim',[1,hor]);

            
            
            if numlev>3 && ~Model.RepQE
                titstr =[num2str(level(id)) ' Effect on ' cell2mat(Model.OutcomePrintNames(i))];
            elseif numlev == 3 && ~Model.RepQE
                if level(id)<0
                    titstr =[cell2mat(Model.OutcomePrintNames(i)) ' to FFT Change -.25'];
                else
                    titstr =[cell2mat(Model.OutcomePrintNames(i)) ' to FFT Change .25'];
                end
            elseif numlev == 2 && ~Model.RepQE
                titstr =['Effect on ' cell2mat(Model.OutcomePrintNames(i))];
            else % Model.RepQE == true
                    titstr =[cell2mat(Model.OutcomePrintNames(i)) ' to QE Surprise'];
            end
            title(titstr);         
            ylabel('Percent');
            ii = ii + 1;
        end

        % decide if graphics window is full and open new window if needed
        if mod(pli,figPerPlot)==0 ||figPerPlot==1 || (i==numresp && ii>=length(level)-1) 
            % first print current window to pdf file
            
            if strcmp('Probit',Model.PScore) && ~(figPerPlot==3) || figPerPlot ==1;
               % Model.LinRes || strcmp('Probit',Model.PScore);
                PrintOr = 'Landscape';
            else
                PrintOr = Model.PrintOr;
            end

                    switch PrintOr
                        case 'Landscape'
                             if figPerPlot==1 % if there is only one plot, reduce paper size to avoid scaling in LaTeX
                                 scrsz = get(gcf,'PaperSize');
                                 set(gcf,'PaperSize',[scrsz(2)/2, scrsz(1)/2]); %enters manual mode - switch axis to get Landscape
                                 set(gcf,'PaperPosition',[0, 0, scrsz(2)/2, scrsz(1)/2]);            
                             elseif figPerPlot==2 && Model.SlideMode % if there is only one plot, reduce paper size to avoid scaling in LaTeX
                                 scrsz = get(gcf,'PaperSize');
                                 set(gcf,'PaperSize',[scrsz(2), scrsz(1)/2]); %enters manual mode - switch axis to get Landscape
                                 set(gcf,'PaperPosition',[0, 0, scrsz(2), scrsz(1)/2]);                                               
                                 %set(gcf,'PaperOrientation','landscape');                 
                             elseif Model.SlideMode
                                 scrsz = get(gcf,'PaperSize');
                                 set(gcf,'PaperPosition',[1,1, scrsz(2)*4/5, scrsz(1)*4/5]); %left,bottom,width, hight
                                 set(gcf,'PaperOrientation','landscape');                 

                             else
                                 scrsz = get(gcf,'PaperSize');
                                 set(gcf,'PaperPosition',[0, -.5, scrsz(2), scrsz(1)]);
                                 set(gcf,'PaperOrientation','landscape');                 
                             end
                        case 'Portrait'
                             scrsz = get(gcf,'PaperSize');
                             %set(gcf,'PaperPosition',[.5, .5, scrsz(1)-1, scrsz(2)-1]) %position image on 8x11 inch paper
                             if figPerPlot==3
                                 set(gcf,'PaperPosition',[1.5,-.95, scrsz(1)-3, scrsz(2)+1.2]) %position image on 8x11 inch paper
                             else
                                set(gcf,'PaperPosition',[-.5,-.95, scrsz(1)+1, scrsz(2)+1.2]) %position image on 8x11 inch paper
                             end
                             set(gcf,'PaperOrientation','portrait'); % print orientation
                    end
                             set(gcf,'PaperPositionMode','manual');  % switch off automatic mode so that desired position obtains
                     if Model.LinRes
                         tstr = ['LinRes_HT' Model.PsStart(end-7:end) '_' Model.PsEnd(end-7:end) ...
                                 '_HT' Model.HTStart(end-7:end) '_' Model.HTEnd(end-7:end)  ];
                     else
                         tstr = ['_PS' Model.PsStart(end-7:end) '_' Model.PsEnd(end-7:end) ...
                                 '_HT' Model.HTStart(end-7:end) '_' Model.HTEnd(end-7:end)  ];
                     end
                     if isfield(Model,'CondImpVarN')
                         if ~isempty(Model.CondImpVal);
                            tstr = [tstr 'CondVar' Model.CondImpVarN num2str(Model.CondImpVal) Model.ReportH];
                         else 
                            tstr = [tstr 'Uncond' Model.ReportH]; 
                         end
                     end
                     if Model.ReportFFED        
                         tstr   = [tstr 'FFED'];
                     end
                     if Model.MulHTEpar.Truncate        
                         tstr   = [tstr 'Trunc'];
                     end
                     if Model.MulHTEpar.Trimm
                         tstr   = [tstr 'Trimm'];
                     end                     
                     if ~Model.MulHTEpar.Trimm && ~Model.MulHTEpar.Truncate        
                         tstr   = [tstr 'NoTreat'];
                     end             
                     tstr = [tstr Model.DemeanMethod];                         
                     if strcmp(Model.PlotType,'Cumulative')
                        tstr = [tstr 'Cum'];
                     else
                        tstr = [tstr 'Ind'];
                     end
                     if Model.SlideMode
                        tstr    = ['Slides_' Model.Type  Model.PScore tstr '_Table_' num2str(tabNo) '.pdf'];
                     else
                        tstr    = [Model.Type  Model.PScore tstr '_Table_' num2str(tabNo) '.pdf'];
                     end
                     switch respType                         
                         case 'MacroVAR' 
                             if Model.VARReportVARImp 
                                saveas(gcf,[Model.Type '_VARIMP' tstr '_Table_' num2str(tabNo) '.pdf'],'pdf');  % save current graph as pdf file
                               % saveas(gcf,[Model.Type '_VARIMP' tstr '_Table_' num2str(tabNo) '.fig'],'fig');  % save current graph as matlab figure
                             else
                                saveas(gcf,tstr,'pdf');  % save current graph as pdf file
                               % saveas(gcf,[Model.Type  Model.PScore tstr '_Table_' num2str(tabNo) '.fig'],'fig');  % save current graph as matlab figure
                             end
                         case 'Macro' 
                            saveas(gcf,tstr,'pdf');  % save current graph as pdf file
                            %saveas(gcf,[Model.Type Model.PScore tstr '_Table_' num2str(tabNo) '.fig'],'fig');  % save current graph as Matlab figure
                         case 'YC'
                            saveas(gcf,tstr,'pdf');  % save current graph as pdf file
                            %saveas(gcf,[Model.Type Model.PScore tstr '_Table_' num2str(tabNo) '.fig'],'fig');  % save current graph as Matlab figure
                     end                                                 
                     tabNo = tabNo + 1;
            if ~(i==numresp && ii==length(level)-1)         
            % Now open new window unless at the end of the loop - overwrites gcf 
                   j    = j+1; %open graphics window number j         
                   h(j) = figure('Visible','off');
                   pli  = 0;               
            end
        end
    end
end


% Reset Parameter values for summary graphs

respType   = Model.RespType;
hor        = Model.ImpHorizon;
numlev     = Model.numlev;  
level      = fliplr(Model.level')'; % report rate increses first

if numlev == 5 && Model.Rep25 && ~Model.RepNeg25
    figPerPlot = 2;
elseif Model.RepNeg25
    %level = level((numlev-1)/2+1:end-1,1); % only report one direction of response 
    %numlev= 2;
else
    figPerPlot = 2;
    %figPerPlot = numlev-1;
end

if strcmp('Probit',Model.PScore) || Model.RepNeg25;
    %Model.LinRes || strcmp('Probit',Model.PScore);
   figPerPlot = 1;
   PrintOr = 'Landscape';
end



%if Model.LinRes 
%    numlev = 2;
%end

numrep   = sum(Model.DoReportList); 
Gamma    = zeros(hor,numrep);
GammaSTD = zeros(hor,numrep);

switch Model.RespType
   case {'MacroVar'}

   case {'YC'}
       pli=0;   
       for jj = numlev-1:-1:1       
        if (~((numlev == 5 && Model.Rep25 && (jj==1 || jj==4))) &&...
            ~((numlev == 5 && Model.RepNeg25 && (jj==1 || jj==3 || jj==4))))
            ii = 1;
            for i = 1:numresp
                if Model.DoReportList(i) 
                    if strcmp(Model.PlotType,'Cumulative') || strcmp(Model.PlotType,'DoubleCum');
                       Gamma(:,ii)    = Model.result(i).gc(:,jj);
                       GammaSTD(:,ii) = Model.result(i).gcs(:,jj);
                    elseif strcmp(Model.PlotType,'Individual');
                       Gamma(:,ii)    = Model.result(i).g(:,jj);
                       GammaSTD(:,ii) = Model.result(i).gs(:,jj);
                    else
                        error('Unsupported PlotType');
                    end
                    ii = ii + 1;
                end
            end
            
            plotvalsdn10 = Gamma-1.645*GammaSTD;
            plotvalsup10 = Gamma+1.645*GammaSTD;
            
            plotvalsdn5 = Gamma-1.96*GammaSTD;
            plotvalsup5 = Gamma+1.96*GammaSTD;

            
            zero10      = ~logical((plotvalsdn10<=0).*(plotvalsup10>=0)); %significant at 10%
            zero5       = ~logical((plotvalsdn5<=0).*(plotvalsup5>=0));   %significant at 5%
            
            zero10      = logical(zero10 - zero5);
            
            Gamma10     = NaN(size(Gamma));
            Gamma5      = NaN(size(Gamma));
            NilData     = NaN(size(Gamma,1),2);
            
            Gamma10(zero10)     = Gamma(zero10);
            Gamma5(zero5)       = Gamma(zero5);
            
            le=ceil(sqrt(figPerPlot));
            wi=ceil(figPerPlot/le);

            pli=pli+1;
            if mod(pli,figPerPlot)==1 ||figPerPlot==1
                   j=j+1; %open graphics window number j
                   h(j)=figure('Visible','off');
                   pli=1;
            end

            if mod(pli,figPerPlot)>0       
                    subplot(le,wi,mod(pli,figPerPlot));
            else
                    subplot(le,wi,figPerPlot);
            end
            if jj >= Model.zp
                id = numlev-jj;
            else
                id = numlev-jj+1;
            end
            
            if Model.YCSummaryColor
            
                    LegendNames = Model.OutcomePrintNames(Model.DoReportList,:);
%                    LegendNames(5,1) = cellstr('10% sig');
%                    LegendNames(6,1) = cellstr('5% sig');

                    col1      = get(gca,'ColorOrder');
                    p0 = plot((1:hor)',Gamma,'LineWidth',2.22);
                    hold on
%{
                    p1 = plot((1:hor)',NilData(:,1),'-kd','LineWidth',1.22,'MarkerSize',10);
                    hold on
                    p2 = plot((1:hor)',NilData(:,1),'-kd','LineWidth',1.22,'MarkerEdgeColor','k',...
                            'MarkerFaceColor','k',...
                            'MarkerSize',10);   

                    leg1 = legend([p0;p1;p2],LegendNames,'Location','SouthEastOutside');
%}                    
                    leg1 = legend(p0,LegendNames,'Location','NorthEast');
                    set(leg1, 'Box', 'off');
                    set(leg1, 'Color', 'none');            
                    hold on

                    hold on



                    for i = 1:size(Gamma10,2) 
                        plot((1:hor)',Gamma10(:,i),'-o','Color',col1(i,:),'LineWidth',1.22,'MarkerSize',6);            
                        hold on
                        plot((1:hor)',Gamma5(:,i),'-o','Color',col1(i,:),'LineWidth',1.22,'MarkerEdgeColor',col1(i,:),...
                            'MarkerFaceColor',col1(i,:),...
                            'MarkerSize',6);            
                        hold on
                    end
                    hold off
                    
            else %Black and White
                    LegendNames = Model.OutcomePrintNames;
                    LegendNames(5,1) = cellstr('10% sig');
                    LegendNames(6,1) = cellstr('5% sig');
                    set(0,'DefaultAxesColorOrder',[0.1 0.1 0.1],...
                        'DefaultAxesLineStyleOrder','-|-.|--|:');
                    p0 = plot((1:hor)',Gamma,'LineWidth',1.22);
                    hold on

                    %cs=(['- ';'-.';'--';': ']);
                    p1 = plot((1:hor)',NilData(:,1),'-k','LineWidth',3);
                    hold on
                    p2 = plot((1:hor)',NilData(:,1),'-k','LineWidth',6);

                    leg1 = legend([p0;p1;p2],LegendNames,'Location','SouthEastOutside');
                    set(leg1, 'Box', 'off');
                    set(leg1, 'Color', 'none');            
                    hold on

                    hold on

%strtrim(cs(i,1))

                    for i = 1:size(Gamma10,2) 
                        plot((1:hor)',Gamma10(:,i),'-','LineWidth',3);            
                        hold on
                        plot((1:hor)',Gamma5(:,i),'-','LineWidth',6);
                        hold on
                    end
                    hold off

            end
            
            grid on       
            if hor<=12
                set(gca,'XTick',(2:2:hor));
            else
                set(gca,'XTick',(3:3:hor));
            end
            set(gca,'XLim',[1,hor])  
            if ~(numlev == 5 && Model.Rep25)
                set(gca,'YLIM',[min(mins),max(maxs)]);
            end
                %axis tight
  
                
            if ~strcmp('Probit',Model.PScore)
                titstr =['Estimated Yield Curve Response to ' num2str(level(id)) ' FFT Change'];
            else
                if level(id)<0
                    titstr ='Estimated Yield Curve Response to Drop in FFT';
                else
                    titstr ='Yield Curve Response to Fed Target Change of Up';
                end
            end
            title(titstr); 
            xlabel('Horizon in Months');
            ylabel('Percent');        
        end %if ~
       end %for jjj
%       scrsz = get(gcf,'PaperSize');
%       set(gcf,'PaperPosition',[1.5, .5, scrsz(1), scrsz(1)-1])
%       set(gcf,'PaperOrientation','landscape');
%       set(gcf,'PaperPositionMode','manual');

       switch PrintOr
           case 'Landscape'
                 if figPerPlot==1 % if there is only one plot, reduce paper size to avoid scaling in LaTeX
                     scrsz = get(gcf,'PaperSize');
                     set(gcf,'PaperSize',[scrsz(2)/2, scrsz(1)/2]); %enters manual mode - switch axis to get Landscape
                     set(gcf,'PaperPosition',[0, 0, scrsz(2)/2, scrsz(1)/2])                                               
                 else
                     scrsz = get(gcf,'PaperSize');
                     set(gcf,'PaperPosition',[0, -.5, scrsz(2), scrsz(1)])
                     set(gcf,'PaperOrientation','landscape');                 
                 end
            case 'Portrait'
                 scrsz = get(gcf,'PaperSize');
                 %set(gcf,'PaperPosition',[.5, .5, scrsz(1)-1, scrsz(2)-1]) %position image on 8x11 inch paper
                 set(gcf,'PaperPosition',[-.5,-.95, scrsz(1)+1, scrsz(2)+1.2]) %position image on 8x11 inch paper
                 set(gcf,'PaperOrientation','portrait'); % print orientation
       end

       if Model.LinRes
         tstr = ['LinRes_HT' Model.PsStart(end-7:end) '_' Model.PsEnd(end-7:end) ...
                 '_HT' Model.HTStart(end-7:end) '_' Model.HTEnd(end-7:end)  ];
       else
         tstr = ['_PS' Model.PsStart(end-7:end) '_' Model.PsEnd(end-7:end) ...
                 '_HT' Model.HTStart(end-7:end) '_' Model.HTEnd(end-7:end)  ];
       end
       if isfield(Model,'CondImpVarN')
         if ~isempty(Model.CondImpVal);
            tstr = [tstr 'CondVar' Model.CondImpVarN num2str(Model.CondImpVal) Model.ReportH];
         else 
            tstr = [tstr 'Uncond' Model.ReportH]; 
         end
       end
       if Model.ReportFFED        
           tstr   = [tstr 'FFED'];
       end
       if Model.MulHTEpar.Truncate        
           tstr   = [tstr 'Trunc'];
       end
       if Model.MulHTEpar.Trimm
           tstr   = [tstr 'Trimm'];
       end                     
       if ~Model.MulHTEpar.Trimm && ~Model.MulHTEpar.Truncate        
           tstr   = [tstr 'NoTreat'];
       end                            
       tstr = [tstr Model.DemeanMethod];
       if strcmp(Model.PlotType,'Cumulative')
             tstr = [tstr 'Cum'];
       else
             tstr = [tstr 'Ind'];
       end
       saveas(gcf,['YC_Summary' Model.Type Model.PScore tstr '.pdf'],'pdf');  % save current graph as pdf file
       % saveas(gcf,['YC_Summary' Model.Type Model.PScore tstr '.fig'],'fig');  % save current graph as pdf file
end
return