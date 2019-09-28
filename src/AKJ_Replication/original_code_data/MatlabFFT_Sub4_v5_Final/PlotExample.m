predChange = random('bino',1,.5,30,1);
actual     = random('unif',0,1,30,1);
MacroVar   = (1:30)' + random('unif',0,1,30,1);
grid on
scatter(1:30,predChange,50,[0 0 0]); % black circles not filled
hold on        
scatter(1:30,actual,50,[0.35 0.35 0.35],'filled'); %dark gray
set(gca,'YLim',[-.1,1.1]);

ylabel('Target Change');    
        
h1 = gca;

h2 = axes('Position',get(h1,'Position'));
plot(h2,1:30,MacroVar,'LineWidth',1.22);

set(h2,'YAxisLocation','right','Color','none','XTickLabel',[]); % label plot on the right, turn of X lables
set(h2,'XLim',get(h1,'XLim'),'Layer','top');                    % use same X limits as on scatter
        
set(h2,'XTick',1:30);  %sets tick spacing on x axis in terms of date var
hold off   
titstr ='Actual and Predicted Change of the Target Rate';
title(titstr); 
ylabel('Monthly IP Growth Rate 2-Sided Average in %');
            