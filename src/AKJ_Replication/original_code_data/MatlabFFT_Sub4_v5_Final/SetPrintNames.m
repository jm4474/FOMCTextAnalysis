function PrintNames = SetPrintNames(OutcomeVarN)

%This function contains definitions of Data-set variable names to names
%used in titles for graphical output
%OutcomeVarN is a cell arry of variable names

PrintNames  = cell(length(OutcomeVarN),1);


for i=1:length(OutcomeVarN)
    if     strcmp(OutcomeVarN(i,1),'RIFLGFCM03')
             PrintNames(i,1) = cellstr('3 Month T-Bill');
    elseif strcmp(OutcomeVarN(i,1),'RIFLGFCM06')
             PrintNames(i,1) = cellstr('6 Month');
    elseif strcmp(OutcomeVarN(i,1),'RIFLGFCY01')
             PrintNames(i,1) = cellstr('1 Year');
    elseif strcmp(OutcomeVarN(i,1),'RIFLGFCY02')
             PrintNames(i,1) = cellstr('2 Year T-Bond');
    elseif strcmp(OutcomeVarN(i,1),'RIFLGFCY03')
             PrintNames(i,1) = cellstr('3 Year');
    elseif strcmp(OutcomeVarN(i,1),'RIFLGFCY05')
             PrintNames(i,1) = cellstr('5 Year T-Bond');
    elseif strcmp(OutcomeVarN(i,1),'RIFLGFCY07')
             PrintNames(i,1) = cellstr('7 Year');
    elseif strcmp(OutcomeVarN(i,1),'RIFLGFCY10')
             PrintNames(i,1) = cellstr('10 Year T-Bond');
    elseif strcmp(OutcomeVarN(i,1),'RIFLGFCY30')
             PrintNames(i,1) = cellstr('30 Year');
    elseif strcmp(OutcomeVarN(i,1),'RIFSPFF')
             PrintNames(i,1) = cellstr('Federal Funds Rate');                 
    elseif strcmp(OutcomeVarN(i,1),'FAAA')
             PrintNames(i,1) = cellstr('AAA');
    elseif strcmp(OutcomeVarN(i,1),'FBAA')
             PrintNames(i,1) = cellstr('BAA');
    elseif strcmp(OutcomeVarN(i,1),'IP')
             PrintNames(i,1) = cellstr('IP');           
    elseif strcmp(OutcomeVarN(i,1),'IPN')
             PrintNames(i,1) = cellstr('IP');                        
    elseif strcmp(OutcomeVarN(i,1),'PCU')
             PrintNames(i,1) = cellstr('Inflation');             
    elseif strcmp(OutcomeVarN(i,1),'PCUN')
             PrintNames(i,1) = cellstr('Inflation');                          
    elseif strcmp(OutcomeVarN(i,1),'JCXFEBM')
             PrintNames(i,1) = cellstr('Inflation');             
    elseif strcmp(OutcomeVarN(i,1),'PCUsLFE')
             PrintNames(i,1) = cellstr('Inflation');
    elseif strcmp(OutcomeVarN(i,1),'PZRAW')
             PrintNames(i,1) = cellstr('PZRAW');
    elseif strcmp(OutcomeVarN(i,1),'FFED')
             PrintNames(i,1) = cellstr('Federal Funds Rate');
    elseif strcmp(OutcomeVarN(i,1),'FARAT')
             PrintNames(i,1) = cellstr('Total Reserves');
    elseif strcmp(OutcomeVarN(i,1),'FARAN')
             PrintNames(i,1) = cellstr('Nonborrowed Reserves');
    elseif strcmp(OutcomeVarN(i,1),'UNRATE')
             PrintNames(i,1) = cellstr('Unemployment');
    elseif strcmp(OutcomeVarN(i,1),'UNRATENSA')
             PrintNames(i,1) = cellstr('Unemployment');             
    elseif strcmp(OutcomeVarN(i,1),'CE16OV_20110708')
             PrintNames(i,1) = cellstr('Civilian Employment'); 
    elseif strcmp(OutcomeVarN(i,1),'CE16OVNSA')
             PrintNames(i,1) = cellstr('Civilian Employment');              
    elseif strcmp(OutcomeVarN(i,1),'AJK1')
             PrintNames(i,1) = cellstr('FFF'); 
    elseif strcmp(OutcomeVarN(i,1),'AJK1sq')
             PrintNames(i,1) = cellstr('FFFsq'); 
    elseif strcmp(OutcomeVarN(i,1),'LastChange')
             PrintNames(i,1) = cellstr('\$Delta&FOMC(-1)');              
    elseif strcmp(OutcomeVarN(i,1),'LastChange')
             PrintNames(i,1) = cellstr('\$Delta&FOMC(-2)');              
    elseif strcmp(OutcomeVarN(i,1),'LastChange')
             PrintNames(i,1) = cellstr('\$Delta&FOMC(-3)');              
    elseif strcmp(OutcomeVarN(i,1),'LastChange')
             PrintNames(i,1) = cellstr('\$Delta&FOMC(-4)');              
    elseif strcmp(OutcomeVarN(i,1),'LastCFOMC')
             PrintNames(i,1) = cellstr('\$Delta&Scheduled');              
    elseif strcmp(OutcomeVarN(i,1),'FOMC Meetings')
             PrintNames(i,1) = cellstr('FOMC');              
    elseif strcmp(OutcomeVarN(i,1),'Trend')
             PrintNames(i,1) = cellstr('a Linear Trend');            
    elseif strcmp(OutcomeVarN(i,1),'IPAGRL')
             PrintNames(i,1) = cellstr('IP Annual Growth Rate');   
    elseif strcmp(OutcomeVarN(i,1),'IPAGRP')
             PrintNames(i,1) = cellstr('IP Annual Growth Rate');                         
    elseif strcmp(OutcomeVarN(i,1),'PCUsLFEAGRL')
             PrintNames(i,1) = cellstr('PCUsLFE Annual Rate');   
    elseif strcmp(OutcomeVarN(i,1),'PCUsLFEAGRP')
             PrintNames(i,1) = cellstr('PCUsLFE Annual Rate');                         

    elseif strcmp(OutcomeVarN(i,1),'IPMGRL')
             PrintNames(i,1) = cellstr('IP Monthly Growth Rate');   
    elseif strcmp(OutcomeVarN(i,1),'IPMGRP')
             PrintNames(i,1) = cellstr('IP Monthly Growth Rate');                         
    elseif strcmp(OutcomeVarN(i,1),'PCUsLFEMGRL')
             PrintNames(i,1) = cellstr('PCUsLFE Monthly Rate');   
    elseif strcmp(OutcomeVarN(i,1),'PCUsLFEMGRP')
             PrintNames(i,1) = cellstr('PCUsLFE Monthly Rate');
    elseif strcmp(OutcomeVarN(i,1),'PCE')
             PrintNames(i,1) = cellstr('PCE');             
    elseif strcmp(OutcomeVarN(i,1),'PCEH')
             PrintNames(i,1) = cellstr('Inflation');             
             
    elseif strcmp(OutcomeVarN(i,1),'CE16OV_20110708MGRP')
             PrintNames(i,1) = cellstr('Civilian Employment Monthly Growth Rate'); 
    elseif strcmp(OutcomeVarN(i,1),'CE16OV_20110708AGRP')
             PrintNames(i,1) = cellstr('Civilian Employment Annual Growth Rate'); 
    elseif strcmp(OutcomeVarN(i,1),'CE16OV_20110708MGRL')
             PrintNames(i,1) = cellstr('Civilian Employment Monthly Growth Rate'); 
    elseif strcmp(OutcomeVarN(i,1),'CE16OV_20110708AGRL')
             PrintNames(i,1) = cellstr('Civilian Employment Annual Growth Rate'); 
             
             
    end
end
             
             
             
             
             
             
             
             
             
             
             

             