function [D,DVarN] = Actual2D(actual,level)

D     = zeros(length(actual),length(level));
DVarN = cell(length(level),1);

for i=1:length(level)
    DVarN(i)  = cellstr(['Target Change ' num2str(level(i))]);
    ind       = find((actual==level(i,1)));
    D(ind,i)  = ones(size(ind,1),1);
end
return