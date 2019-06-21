%% Script to analyze bluebooks

Tbluebook = readtable('../Output/Bluebook/CSV/TableBluebook.csv');

%% Focus on the text data

data      = Tbluebook.TextBluebook;

%% Extract Alternatives (15 seconds)

alternatives ...
            = strings(size(Tbluebook,1),3); 

tic

for t_bbook = 1 :size(Tbluebook,1)

aux        = splitSentences(data(t_bbook,1));

dummyA     = (contains(aux,'Alternative A','IgnoreCase',true)...
           & contains(aux,'federal funds','IgnoreCase',false)) ...
            |(contains(aux,'Alternative A','IgnoreCase',true)...
           & contains(aux,'funds rate','IgnoreCase',false))...
           |(contains(aux,'Alternative A','IgnoreCase',true)...
           & contains(aux,'target','IgnoreCase',false));

auxA       = aux(dummyA);

if isempty(auxA)

alternatives(t_bbook,1) ...
           = 'NO ALTERNATIVE A FOUND';
       
else
    
alternatives(t_bbook,1) ...
           = auxA(1,1);    
end

clear dummyA auxA

dummyB     = (contains(aux,'Alternative B','IgnoreCase',true)...
           & contains(aux,'federal funds','IgnoreCase',false))...
           | (contains(aux,'Alternative B','IgnoreCase',true)...
           & contains(aux,'funds rate','IgnoreCase',false))...
           |(contains(aux,'Alternative B','IgnoreCase',true)...
           & contains(aux,'target','IgnoreCase',false));
           

auxB       = aux(dummyB);

if isempty(auxB)

alternatives(t_bbook,2) ...
           = 'NO ALTERNATIVE B FOUND';
       
else
    
alternatives(t_bbook,2) ...
           = auxB(1,1);    
end

clear dummyB auxB

dummyC     = (contains(aux,'Alternative C','IgnoreCase',true)...
           & contains(aux,'federal funds','IgnoreCase',false))...
           | (contains(aux,'Alternative C','IgnoreCase',true)...
           & contains(aux,'funds rate','IgnoreCase',false))...
           |(contains(aux,'Alternative C','IgnoreCase',true)...
           & contains(aux,'target','IgnoreCase',false));

auxC       = aux(dummyC);

if isempty(auxC)

alternatives(t_bbook,3) ...
           = 'NO ALTERNATIVE C FOUND';
       
else
    
alternatives(t_bbook,3) ...
           = auxC(1,1);    
end

clear dummyC auxC


end

toc

%% Store as CSV

tableaux = table(alternatives(:,1),alternatives(:,2),alternatives(:,3));

Tableaux.Properties.VariableNames ...
         = {'Alternative A', 'Alternative B', 'Alternative C'};
     
Table_alt ...
         = [Tbluebook(:,1:5),tableaux];  
     
clear tableaux

writetable(Table_alt,'../Output/Bluebook/CSV/TableBluebookAlternatives.csv');

clearvars -except Table_alt 



