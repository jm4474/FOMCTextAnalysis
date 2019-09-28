function Model=PlotFit(Model)

numlev     = Model.numlev;
hor        = Model.ImpHorizon;
figPerPlot = numlev+1;
j          = 1;
level      = fliplr(Model.level')'; % report rate increses first
figure('Visible','off');
switch Model.ImpType
   case {'L'}

   case {'NL'}
       fit         = Model.fit;
       NaNM        = NaN(size(fit));
       fit(fit==0) = NaNM(fit==0);
       fit1        = Model.fit1;
       NaNM        = NaN(size(fit1));
       fit1(fit1==0) = NaNM(fit1==0);       
       
       pli=0;   
       for jj = numlev:-1:1       
           le=ceil(sqrt(figPerPlot));
           wi=ceil(figPerPlot/le);

            pli=pli+1;
            if mod(pli,figPerPlot)==1 ||figPerPlot==1
                   j=j+1; %open graphics window number j
                   h(j)=figure;
                   pli=1;
            end

            if mod(pli,figPerPlot)>0       
                    subplot(wi,le,mod(pli,figPerPlot));
            else
                    subplot(wi,le,figPerPlot);
            end

            grid on
            scatter(Model.HTSampDat(1:end-hor),fit(:,jj),10,[0 .56 0],'filled'); % red, use Date variable as x values for easier labling
            hold on        
            scatter(Model.HTSampDat(1:end-hor),fit1(:,jj),10,[1 0 0],'filled'); %dark green
            hold off
            set(gca,'XLim',[Model.HTSampDat(1),Model.HTSampDat(end-hor)]) %defines the limits for the x axes 
            id = numlev-jj+1;
            set(gca,'XTick',Model.SampDat((7:24:length(fit))));  %sets tick spacing on x axis in terms of date var
            datetick('x','yy','keeplimits','keepticks');      %formats date labels and keeps spacing and limits set in prevous line
            if numlev>3
                    titstr =['FFT Change ' num2str(level(id))];
                else
                    if level(id)<0
                        titstr ='FFT Change Down';
                    elseif level(id)>0
                        titstr ='FFT Change Up';
                    else
                        titstr ='No FFT Change';
                    end
                end
                title(titstr); 
            title(titstr); 
            ylabel('Phat');        
           end
    papsz = get(gcf,'PaperSize');
    set(gcf,'PaperPosition',[.5, .5, papsz(2)-1, papsz(1)-1])
    set(gcf,'PaperOrientation','landscape');
    set(gcf,'PaperPositionMode','manual');
    saveas(gcf,[Model.Type 'Fit.pdf'],'pdf');  % save current graph as pdf file        
end
return