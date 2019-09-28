function [TargetRate,DateTargetRate] = FindTargetRate(data,colheaders)

colTR = strcmp(colheaders,'Target Rate');
colY  = strcmp(colheaders,'Year');
colM  = strcmp(colheaders,'Month');
colD  = strcmp(colheaders,'Day');

n     = length(data);
oldm  = data(2,colM);
TargetRate = [];
DateTargetRate = [];

for i=2:n-1
    if data(i+1,colM) ~= oldm || i == n-1
       TargetRate  = [TargetRate;data(i,colTR)];
       DateTR(1,1) = data(i,colY);
       DateTR(1,2) = data(i,colM);
       DateTR(1,3) = data(i,colD);
       DateTargetRate = [DateTargetRate;DateTR];
       oldm       = data(i+1,colM);       
    end
end
        
    