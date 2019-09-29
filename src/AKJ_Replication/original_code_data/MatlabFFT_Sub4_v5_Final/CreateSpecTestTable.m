function table = CreateSpecTestTable(Model,table,append)

if ~isempty(table) && ~append
    colh1 = table.colh1; %contains Estimator Description
    rowh  = table.rowh;
    data  = table.data;
    
    colh1 = [colh1,cellstr(strrep(Model.Type,'_',' '))];
    empfl = false;
    
elseif append

    colh1 = table.colh1; %contains Estimator Description
    rowh  = table.rowh;
    data  = table.data;
    
    empfl = false; %don't add addtional column

else 
    colh1    = cell(1);
    colh1(1) = cellstr(strrep(Model.Type,'_',' '));
    
    rowh    = [Model.SpecTestPrintNames];
    data    = NaN(length(rowh),1);
    empfl   = true;
end

t           = union(rowh,Model.SpecTestPrintNames,'stable'); %combine variable names
[~,ia,~]    = intersect(t,rowh,'stable');
data1       = NaN(length(t),size(data,2));
data1(ia,:) = data;
[~,ia,~]    = intersect(t,Model.SpecTestPrintNames,'stable');
if empfl
    data1(ia,1) = Model.SpecTest;
    %data1(ia,1) = Model.SpecTestStat;
elseif append
    data1(ia,end) = Model.SpecTest;
    %data1(ia,end) = Model.SpecTestStat;
else
    data1         = [data1,NaN(size(data1,1),1)];
    data1(ia,end) = Model.SpecTest;
    %data1(ia,end) = Model.SpecTestStat;
end

table.rowh  = t;
table.data  = data1;
table.colh1 = colh1;
    
    
return