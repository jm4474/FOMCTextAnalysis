function table = PrintDescStatsTable(table,texfn)

% input : structure table generated with CreateSpecTestTable.m
% output: texfn.tex file with table in latex code. table augmented by print formated cell array

rowh    = table.rowh;
colh1   = table.colh1;
colh2   = table.colh2;
data    = table.data;
J       = size(data,2);
I       = size(data,1);
prndata = cell(I,J);

i  = 1;
while i <= I %go through all rows
    j = 1;
    while j<=J
        if ~isnan(data(i,j))
                prstr = num2str(data(i,j),'% -6.3f');
        else
                prstr = '';
        end
        prndata(i,j)  = cellstr(prstr);
        j  = j  + 1;
    end %while j    
    i  = i  + 1;
end %while i
table.prndata = prndata;
if ischar(texfn)
    matrix2latex(prndata, texfn, 'rowLabels', rowh, 'columnLabels', [colh1;colh2],'size', 'small');
else
    error('PrintTable second argument needs to be textstring of the form filename.tex');
end
return