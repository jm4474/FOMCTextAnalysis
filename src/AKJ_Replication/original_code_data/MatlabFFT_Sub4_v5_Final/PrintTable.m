function table = PrintTable(table,texfn)

% input : structure table generated with CreateTable.m
% output: texfn.tex file with table in latex code. table augmented by print formated cell array

rowh    = table.rowh;
data    = table.data;
J       = size(data,2);
I       = size(data,1);
prndata = cell(2*(I-5)+5,J/4);
rowh1   = cell(2*(I-5)+5,1);

i  = 1;
ii = 1;
while i <= I %go through all rows
    j = 1;
    jj = 1;
    while j<=J
        if ~isnan(data(i,j))
            if i<=I-5 % report standard errors for parameters
                prstr        = num2str(data(i,j),'% -6.2f');
                if data(i,j+3)<.01
                    prstr = [prstr,'***'];
                elseif data(i,j+3)<.05
                    prstr = [prstr,'** '];
                elseif data(i,j+3)<.01
                    prstr = [prstr,'*  '];
                else
                    prstr = [prstr,'   '];
                end            
                stdestr   = ['(',num2str(data(i,j+1),'% -6.2f'),')'];
            else %no standard errors for R2, LR, n
                prstr        = num2str(data(i,j),'% -6.2f');
            end
        else
            prstr     = '';
            stdestr   = '';
        end
        prndata(ii,jj)   = cellstr(prstr);
        if i<=I-5
            prndata(ii+1,jj) = cellstr(stdestr);
        end
        jj = jj + 1;
        j  = j  + 4;
    end %while j    
    rowh1(ii,1) = rowh(i,1);
    if i<=I-5
       rowh1(ii+1,1) = cellstr('');
       ii = ii + 2;
    else
       ii = ii + 1;
    end
    i  = i  + 1;
end %while i
table.prndata = prndata;
if ischar(texfn)
    matrix2latex(prndata, texfn, 'rowLabels', rowh1, 'columnLabels', table.colh1,'size', 'small');
else
    error('PrintTable second argument needs to be textstring of the form filename.tex');
end
return