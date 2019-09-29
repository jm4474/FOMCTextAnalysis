function table = CreateTable(Diag,Model,table)

diagnostic = cellstr(['Lik         ';...
                      'Pseudo R2   ';...
                      'LR          ';...
                      'p-val       ';...
                      'Sample Size ';...
                      'Sample Begin';...
                      'Sample End  ';...
                      'HT Begin    ';...
                      'HT End      ']);
                  
SBv  = datevec(Model.Diag.EstStart);
SEv  = datevec(Model.Diag.EstEnd);

SB   = SBv(:,1)*100+SBv(:,2);
SE   = SEv(:,1)*100+SEv(:,2);

HTBv = datevec(Model.Diag.HTStart);
HTEv = datevec(Model.Diag.HTEnd);

HTB  = HTBv(:,1)*100+HTBv(:,2);
HTE  = HTEv(:,1)*100+HTEv(:,2);


if ~isempty(table)
    colh1 = table.colh1; %contains Estimator Description
    colh2 = table.colh2; %contains Column Description
    rowh  = table.rowh;
    data  = table.data;
    
    colh1 = [colh1,cellstr(strrep(Model.Type,'_',' '))];
    colh2 = [colh2,'Param'];
    colh2 = [colh2,'SE'];
    colh2 = [colh2,'t-ratio'];
    colh2 = [colh2,'sig'];
    empfl = false;
    
else 
    colh1    = cell(1);
    colh2    = cell(1,4);
    colh1(1) = cellstr(strrep(Model.Type,'_',' '));
    colh2(1,1) = cellstr('Param');
    colh2(1,2) = cellstr('SE');
    colh2(1,3) = cellstr('t-ratio');
    colh2(1,4) = cellstr('sig');
    
    rowh    = [Diag.XVarN;'Lik';'Pseudo R2';'LR';'p-val';'Sample Size'];
    data    = NaN(length(rowh),4);
    empfl   = true;
end
rowhVar     = setdiff(rowh,diagnostic,'stable'); %reomve columns with diagnostics, stable=keep ordering in rowh
t           = union(rowhVar,Diag.XVarN,'stable'); %combine variable names
t           = [t;diagnostic];                     %reappend diagnostics
[~,ia,~]    = intersect(t,rowh,'stable');
data1       = NaN(length(t),size(data,2));
data1(ia,:) = data;
[~,ia,ib]    = intersect(t,Diag.XVarN,'stable');
if empfl
        if strcmp(Model.PScore,'Oprob')
            NewData     = [[Diag.par;Diag.cut], Diag.stde,Diag.tstat,Diag.pva];
            data1(ia,:) = NewData(ib,:);
        else
            NewData     = [Diag.par, Diag.stde,Diag.tstat,Diag.pva];
            data1(ia,:) = NewData(ib,:);
        end
        if ~isempty(Diag.Lik)
            data1(strcmp(t,'Lik'),1)         = Diag.Lik;       
        end        
        if ~isempty(Diag.PR2)
            data1(strcmp(t,'Pseudo R2'),1)   = Diag.PR2;       
        end
        if ~isempty(Diag.LR)
            data1(strcmp(t,'LR'),1)          = Diag.LR;
        end
        if ~isempty(Diag.pvLR)
            data1(strcmp(t,'p-val'),1)       = Diag.pvLR;
        end
        if ~isempty(Diag.n)
            data1(strcmp(t,'Sample Size'),1) = Diag.nlik;
        end
        if ~isempty(Diag.EstStart)
            data1(strcmp(t,'Sample Begin'),1) = SB;
        end
        if ~isempty(Diag.EstEnd)
            data1(strcmp(t,'Sample End'),1) = SE;
        end
        if ~isempty(Diag.HTStart)
            data1(strcmp(t,'HT Begin'),1) = HTB;
        end
        if ~isempty(Diag.HTEnd)
            data1(strcmp(t,'HT End'),1) = HTE;
        end        
        
else
        data1       = [data1,NaN(size(data1,1),4)];
        if strcmp(Model.PScore,'Oprob')
            NewData             = [[Diag.par;Diag.cut], Diag.stde,Diag.tstat,Diag.pva];
            data1(ia,end-3:end) = NewData(ib,:);
        else
            NewData             = [Diag.par, Diag.stde,Diag.tstat,Diag.pva];
            data1(ia,end-3:end) = NewData(ib,:);
        end
        if ~isempty(Diag.Lik)
            data1(strcmp(t,'Lik'),end-3)             = Diag.Lik;       
        end                
        if ~isempty(Diag.PR2)
            data1(strcmp(t,'Pseudo R2'),end-3)   = Diag.PR2;       
        end
        if ~isempty(Diag.LR)
            data1(strcmp(t,'LR'),end-3)          = Diag.LR;
        end
        if ~isempty(Diag.pvLR)
            data1(strcmp(t,'p-val'),end-3)       = Diag.pvLR;
        end
        if ~isempty(Diag.n)
            data1(strcmp(t,'Sample Size'),end-3) = Diag.nlik;
        end
        if ~isempty(Diag.EstStart)
            data1(strcmp(t,'Sample Begin'),end-3) = SB;
        end
        if ~isempty(Diag.EstEnd)
            data1(strcmp(t,'Sample End'),end-3) = SE;            
        end
        if ~isempty(Diag.HTStart)
            data1(strcmp(t,'HT Begin'),end-3) = HTB;
        end
        if ~isempty(Diag.HTEnd)
            data1(strcmp(t,'HT End'),end-3) = HTE;
        end                
end
data        = data1;
rowh        = t;


 table.colh1 = colh1; %contains Estimator Description
 table.colh2 = colh2; %contains Column Description
 table.rowh  = rowh;
 table.data  = data;
 
 return