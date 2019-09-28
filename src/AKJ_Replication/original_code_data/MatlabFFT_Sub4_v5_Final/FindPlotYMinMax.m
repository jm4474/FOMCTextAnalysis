function [mins,maxs] = FindPlotYMinMax(Model)
% determins Y axis minima and maxima depending on data and model parameters

respType   = Model.RespType;
crit       = Model.ImpRespCrit;
if isfield(Model,'Diag')
    if isfield(Model.Diag,'effnumlev')
        numlev = Model.Diag.effnumlev;
        if Model.MultiNomQE
           numlev = numlev-1;
        end    
    else
        numlev     = Model.numlev;  
    end
else
     numlev     = Model.numlev;  
end


numresp    = size(Model.yM,2);


maxs = zeros(numresp,1);
mins = zeros(numresp,1);

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
        if ~Model.VARReportVARImp
            plotvalsdn = Gamma-crit*GammaSTD;
            plotvalsup = Gamma+crit*GammaSTD;
        end                

        if numlev == 5 && Model.Rep25 
                %numlev == 5 && Model.Rep25 && ~Model.LinRes
                % handle case where only reporting +/- .25% separately 
                maxv = max(max(plotvalsup(:,2:3)));
                minv = min(min(plotvalsdn(:,2:3)));
                if minv > 0
                    minv = .8*minv;
                    maxv = 1.2*maxv;
                elseif maxv > 0
                    minv = 1.2*minv;
                    maxv = 1.2*maxv;
                else
                    maxv = .8*maxv;
                    minv = 1.2*minv;
                end                                   
                mins(i,1) = minv;
                maxs(i,1) = maxv; %store scale for YC summary graphs                
        else
                maxv = max(max(plotvalsup));
                minv = min(min(plotvalsdn));
                if minv > 0
                    minv = .8*minv;
                    maxv = 1.2*maxv;
                elseif maxv > 0
                    minv = 1.2*minv;
                    maxv = 1.2*maxv;
                else
                    maxv = .8*maxv;
                    minv = 1.2*minv;
                end                   
                mins(i,1) = minv;
                maxs(i,1) = maxv;
                
        end
    end
end