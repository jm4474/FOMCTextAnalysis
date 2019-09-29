function Model=PlotFitPredChange(Model)

MacroVarN = Model.FitMacroVarN;
ind       = strcmp(Model.OutcomeVarN,MacroVarN);
MacroVar  = Model.yMFit(:,ind)*100;  % report in % points
if Model.FitMacroSmooth
    n     = size(MacroVar,1);
    MSm   = zeros(n);
    for i = -Model.NumFitSmooth:Model.NumFitSmooth
        MSm = MSm + diag(ones(n-abs(i),1),i);
    end   
    MacroVar = MSm*MacroVar/(2*Model.NumFitSmooth+1);
end
  
figure('Visible','off');
switch Model.ImpType
   case {'L'}

   case {'NL'}
        phat         = Model.Diag.phatps;
        if size(phat,2)==5
            predChange  = phat*[-.5,-.25,0,.25,.5]';
        elseif size(phat,2)==3 
            predChange  = phat*[-.25,0,.25]';
        elseif size(phat,2)==2
            predChange  = phat*[-.25,0]';
        end

        grid on
        g1 = scatter(Model.PsSampDat(1:end),predChange,50,[0 0 0]); % black circles not filled
        hold on        
        g2 = scatter(Model.PsSampDat(1:end),Model.Diag.yps,50,[0.35 0.35 0.35],'filled'); %dark gray
        if size(phat,2)==2
            set(gca,'YLim',[-.3,.1]);
        else
            set(gca,'YLim',[-.6,.6]);
        end
        grid off;
        set(gca,'XLim',[Model.PsSampDat(1),Model.PsSampDat(end)]) %defines the limits for the x axes 
        if length(Model.PsSampDat)<50
            set(gca,'XTick',Model.PsSampDat((1:6:length(Model.Diag.yps))));  %sets tick spacing on x axis in terms of date var
            datetick('x','mm/yy','keeplimits','keepticks');      %formats date labels and keeps spacing and limits set in prevous line
        else
            set(gca,'XTick',Model.PsSampDat((7:24:length(Model.Diag.yps))));  %sets tick spacing on x axis in terms of date var
            datetick('x','yy','keeplimits','keepticks');      %formats date labels and keeps spacing and limits set in prevous line
        end        
        ylabel('Target Change');    
        
        h1 = gca;

 
       
        h2 = axes('Position',get(h1,'Position'));
        g3 = line(Model.PsSampDat(1:end),MacroVar,'LineWidth',1.22);
        
        LegendNames(1,1) = cellstr('Predicted');
        LegendNames(2,1) = cellstr('Actual');
        LegendNames(3,1) = cellstr('IP');
        
        leg1 = legend([g1,g2,g3],LegendNames,'Location','NorthEast');
        set(leg1, 'Box', 'off');
        set(leg1, 'Color', 'none');      
        hold on
        line(Model.PsSampDat(1:end),ones(size(MacroVar,1),1)*max(get(h2,'YLim')),'LineWidth',1.22,'Color','black'); %draw black line on top of graph to close box
        hold on
        set(h2,'YAxisLocation','right','Color','none','XTickLabel',[]); % label plot on the right, turn of X lables
      %  ytick = get(h2,'YTick');                                        % find min and max of YTick to align markers with scatter
      %  set(h2,'YTick',ytick(1):.1:ytick(end),'Layer','top');                         % align markers with scatter
      %  set(h1,'YTick',-.3:.05:.1,'Layer','top');      
        set(h2,'XLim',get(h1,'XLim'),'Layer','top');                    % use same X limits as on scatter
        if length(Model.PsSampDat)<50
            set(h2,'XTick',Model.PsSampDat((1:6:length(Model.Diag.yps))));  %sets tick spacing on x axis in terms of date var
            datetick('x','mm/yy','keeplimits','keepticks');      %formats date labels and keeps spacing and limits set in prevous line
        else
            set(h2,'XTick',Model.PsSampDat((7:24:length(Model.Diag.yps))));  %sets tick spacing on x axis in terms of date var
            datetick('x','yy','keeplimits','keepticks');      %formats date labels and keeps spacing and limits set in prevous line
        end        
        hold off   
        titstr ='Actual and Predicted Change of the Target Rate';
        title(titstr); 
        ylabel('Monthly IP Growth Rate 2-Sided Average in %');
            

    papsz = get(gcf,'PaperSize');
    set(gcf,'PaperPosition',[0, -.5, papsz(2)-1, papsz(1)-1])
    set(gcf,'PaperOrientation','landscape');
    set(gcf,'PaperPositionMode','manual');
    saveas(gcf,[Model.Type 'Fit.pdf'],'pdf');  % save current graph as pdf file        
end
return