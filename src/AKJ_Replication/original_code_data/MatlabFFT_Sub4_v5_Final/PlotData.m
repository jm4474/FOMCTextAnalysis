function Model=PlotData(Model)

dat        = (Model.LevelRespDate);
LevDat     = Model.LevelRespData(:,1:4); %Don't plot FFED
TargetRate = Model.TargetRate;

LegendNames(1,1) = cellstr('3 Month');
LegendNames(2,1) = cellstr('2 Year');
LegendNames(3,1) = cellstr('5 Year');
LegendNames(4,1) = cellstr('10 Year');
LegendNames(5,1) = cellstr('Target Rate');



h = figure;
grid on

p0=plot(dat,LevDat); 
set(p0,'LineWidth',1.5);
hold on        ;
grid on

ts1 = timeseries(TargetRate,dat);
ts1 = setinterpmethod(ts1, 'zoh');

p1=plot(ts1,'-b'); 

%p1=plot(dat,TargetRate,'-b'); 
hold off

set(p1,'Color','black','LineWidth',2);
set(gca,'XLim',[dat(1),dat(end)]) %defines the limits for the x axes 

set(gca,'XTick',dat(1:24:length(dat)));  %sets tick spacing on x axis in terms of date var
datetick('x','yy','keeplimits','keepticks');      %formats date labels and keeps spacing and limits set in prevous line
title('Interest Rate Data'); 
ylabel('Percent');  
xlabel('Year');

leg1 = legend([p0;p1],LegendNames,'Location','NorthEast');
set(leg1, 'Box', 'off');
set(leg1, 'Color', 'none');            
hold on

scrsz = get(gcf,'PaperSize');
set(gcf,'PaperPosition',[.5, .5, scrsz(2)*9/10, scrsz(1)*9/10]);
set(gcf,'PaperOrientation','landscape');                
%papsz = get(gcf,'PaperSize');
%set(gcf,'PaperPosition',[.5, .5, papsz(2)-1, papsz(1)-1])
%set(gcf,'PaperOrientation','landscape');
set(gcf,'PaperPositionMode','manual');
saveas(gcf,['Slides_YieldData.pdf'],'pdf');  % save current graph as pdf file        

return
