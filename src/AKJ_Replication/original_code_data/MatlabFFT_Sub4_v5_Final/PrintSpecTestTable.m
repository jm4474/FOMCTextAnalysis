function table = PrintSpecTestTable(table,texfn)

% input : structure table generated with CreateSpecTestTable.m
% output: texfn.tex file with table in latex code. table augmented by print formated cell array

rowh    = table.rowh;
data    = table.data;
J       = size(data,2);
I       = size(data,1);
prndata = cell(I,J);

i  = 1;
while i <= I %go through all rows
    j = 1;
    while j<=J
        if ~isnan(data(i,j))
                if data(i,j)<1
                    prstr        = num2str(data(i,j),'% -6.3f');
                else
                    prstr        = '    .   ';
                end
                if data(i,j)<.01
                    prstr = [prstr,'   '];
                elseif data(i,j)<.05
                    prstr = [prstr,'   '];
                elseif data(i,j)<.1
                    prstr = [prstr,'   '];
                else
                    prstr = [prstr,'   '];
                end            
        else
            prstr     = '';
            stdestr   = '';
        end
        prndata(i,j)   = cellstr(prstr);
        j  = j  + 1;
    end %while j    
    i  = i  + 1;
end %while i
table.prndata = prndata;
if ischar(texfn)
    matrix2latex(prndata, texfn, 'rowLabels', rowh, 'columnLabels', table.colh1,'size', 'small');
else
    error('PrintTable second argument needs to be textstring of the form filename.tex');
end
return
