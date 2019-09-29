function [ind,numd]=lastDayOfMonth(y)
ind=[];
numd=[];
[year,month,day]=datevec(y);
eomd=eomday(year,month);
for i=2:size(y,1)+1
    if  i<=size(y,1)
        if month(i)~=month(i-1)
           ind=[ind;i-1];
           numd=[numd; datenum([year(i-1),month(i-1),eomd(i-1)])];
        end
    else %record last month in the sample
       ind=[ind;i-1];
       numd=[numd; datenum([year(i-1),month(i-1),eomd(i-1)])]; 
    end
end
return
    

