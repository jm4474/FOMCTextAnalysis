function PrintNames =SetDoNotPrintList(Type,OutcomeVarN,ReportFFED)

%This function contains definitions of Data-set variable names to names
%used in titles for graphical output
%OutcomeVarN is a cell arry of variable names

PrintNames  = true(length(OutcomeVarN),1); % Default set all variables to print

if ~isempty(strfind(Type,'Macro_'))
        for i=1:length(OutcomeVarN)
 %uncomment variable names to exclude them from being reported on impulse response graphs           
                %{
            if      strcmp(OutcomeVarN(i,1),'RIFLGFCM03')
                     PrintNames(i,1) = false;
            elseif strcmp(OutcomeVarN(i,1),'RIFLGFCM06')
                     PrintNames(i,1) = false;
            elseif strcmp(OutcomeVarN(i,1),'RIFLGFCY01')
                     PrintNames(i,1) = false;
            elseif strcmp(OutcomeVarN(i,1),'RIFLGFCY02')
                     PrintNames(i,1) = false;
            elseif strcmp(OutcomeVarN(i,1),'RIFLGFCY03')
                     PrintNames(i,1) = false;
             elseif strcmp(OutcomeVarN(i,1),'RIFLGFCY05')
                     PrintNames(i,1) = false;                    
            elseif strcmp(OutcomeVarN(i,1),'RIFLGFCY07')
                     PrintNames(i,1) = false;
            elseif strcmp(OutcomeVarN(i,1),'RIFLGFCY10')
                     PrintNames(i,1) = false;
            elseif strcmp(OutcomeVarN(i,1),'RIFLGFCY30')
                     PrintNames(i,1) = false;
            elseif strcmp(OutcomeVarN(i,1),'FAAA')
                     PrintNames(i,1) = false;
            elseif strcmp(OutcomeVarN(i,1),'FBAA')
                     PrintNames(i,1) = false;
             elseif strcmp(OutcomeVarN(i,1),'PZRAW')
                     PrintNames(i,1) = false;

                      
            else
 %}
            if strcmp(OutcomeVarN(i,1),'FARAT')
                     PrintNames(i,1) = false;
            elseif strcmp(OutcomeVarN(i,1),'FARAN')
                     PrintNames(i,1) = false;
 %           elseif strcmp(OutcomeVarN(i,1),'UNRATE')
                     PrintNames(i,1) = false;                     
            elseif ReportFFED && strcmp(OutcomeVarN(i,1),'IP')
                     PrintNames(i,1) = false;          
            elseif ReportFFED && strcmp(OutcomeVarN(i,1),'PCE')
                     PrintNames(i,1) = false;                             
            elseif ReportFFED && strcmp(OutcomeVarN(i,1),'PCEH')
                     PrintNames(i,1) = false;                                                  
            elseif ReportFFED && strcmp(OutcomeVarN(i,1),'IPN')
                     PrintNames(i,1) = false;                                
            elseif ReportFFED && strcmp(OutcomeVarN(i,1),'PCU')
                     PrintNames(i,1) = false;
            elseif ReportFFED && strcmp(OutcomeVarN(i,1),'PCUN')
                     PrintNames(i,1) = false;                     
            elseif ReportFFED && strcmp(OutcomeVarN(i,1),'PCUsLFE')
                     PrintNames(i,1) = false;
            elseif ReportFFED && strcmp(OutcomeVarN(i,1),'Trend')
                     PrintNames(i,1) = false;     
                     
            elseif ReportFFED && strcmp(OutcomeVarN(i,1),'PCUsLFEMGRL')
                     PrintNames(i,1) = false;     
            elseif ReportFFED && strcmp(OutcomeVarN(i,1),'PCUsLFEAGRL')
                     PrintNames(i,1) = false;     
            elseif ReportFFED && strcmp(OutcomeVarN(i,1),'IPMGRL')
                     PrintNames(i,1) = false;     
            elseif ReportFFED && strcmp(OutcomeVarN(i,1),'IPAGRL')
                     PrintNames(i,1) = false;     
                     
            elseif ~ReportFFED && strcmp(OutcomeVarN(i,1),'FFED')               
                     PrintNames(i,1) = false;
            elseif ReportFFED && strcmp(OutcomeVarN(i,1),'UNRATE')                     
                     PrintNames(i,1) = false;
            elseif ReportFFED && strcmp(OutcomeVarN(i,1),'UNRATENSA')                     
                     PrintNames(i,1) = false;                     
            elseif ReportFFED && strcmp(OutcomeVarN(i,1),'CE16OV_20110708')
                     PrintNames(i,1) = false;                     
           elseif ReportFFED && strcmp(OutcomeVarN(i,1),'CE16OVNSA')
                     PrintNames(i,1) = false;                                          
            elseif ReportFFED && strcmp(OutcomeVarN(i,1),'CE16OV_20110708MGRL')
                     PrintNames(i,1) = false;                     
            elseif ReportFFED && strcmp(OutcomeVarN(i,1),'CE16OV_20110708AGRL')
                     PrintNames(i,1) = false;                     

%{          
           
            elseif strcmp(OutcomeVarN(i,1),'CE16OV_20110708')
                     PrintNames(i,1) = false;        
%}                     
            end
        end
elseif ~isempty(strfind(Type,'YC_'))
    for i=1:length(OutcomeVarN)
            if      strcmp(OutcomeVarN(i,1),'RIFSPFF')
                     PrintNames(i,1) = false;
            elseif strcmp(OutcomeVarN(i,1),'RIFLGFCY05')
                     PrintNames(i,1) = false;
            end
    end
end
             
             
             
             
             
             
             
             
             
             
             

             