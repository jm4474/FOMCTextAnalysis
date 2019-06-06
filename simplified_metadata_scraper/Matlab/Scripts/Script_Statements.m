T = readtable('../Output/FedCorpus_derived.csv');

%% Select Statements

Tstatements = T(strcmp(T.Name,'Statement'),:);

%% Urls for statements

root = 'https://www.federalreserve.gov';

url  = string(strcat(root,Tstatements.Links));

%%

webread(url(6))