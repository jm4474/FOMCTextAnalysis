function table = Create_ImpulseResponse_Table(Model,table)

    ch2(1) = cellstr('-.25');
    ch2(2) = cellstr('sig');
    ch2(3) = cellstr('+.25');
    ch2(4) = cellstr('sig');
    
    OutcomeVarN = Model.OutcomeVarN;
 

if ~isempty(table) 
    colh1 = table.colh1; %contains Test Description
    colh2 = table.colh2;
    rowh  = table.rowh;
    data  = table.data;
    
else 
    colh1    = [];
    colh2    = cell(1);
    rowh     = cell(24,1);
    for i=1:24
        rowh(i,1)    = cellstr(num2str(i)); 
    end
    data    =      NaN(24,length(colh1));   
end

if Model.ReportFFED
    t           = union('FFED',colh1,'stable'); %combine variable names
    [~,ia,~]    = intersect(t,colh1,'stable');
    data1       = NaN(24,length(t)*4);
    for i=1:length(ia)  %copy previous data
        data1(:,(ia(i)-1)*4+1:ia(i)*4) = data(:,(i-1)*4+1:i*4);
    end
    [~,ia,~]    = intersect(t,'FFED','stable');    
    [~,~,ib]    = intersect('FFED',Model.OutcomeVarN,'stable'); %Model.OutcomeVarN delivers pointer to data-set
    lcolh2      = length(colh2);
    colh2       = [colh2;cell(4*length(ib),1)];
    for j       = 1:length(ib) % # of new variables added to table
        colh2((lcolh2+(j-1)*4+1):(lcolh2+j*4),1)   = ch2;
    end
else
    if ~isempty(intersect('FFED',OutcomeVarN))
        OutcomeVarN = setdiff(OutcomeVarN,'FFED','stable');
    else
        OutcomeVarN = OutcomeVarN;
    end
    if isempty(colh1)
        t       =     OutcomeVarN;
    else
        t       =     union(colh1,OutcomeVarN,'stable'); %combine variable names
    end
    [~,~,ib]    = intersect(colh1,OutcomeVarN,'stable');
    lcolh2      = length(colh2);
    colh2       = [colh2;cell(4*length(ib),1)];
    for j       = 1:length(OutcomeVarN)-length(ib)
        colh2((lcolh2+(j-1)*4+1):(lcolh2+j*4),1)   = ch2;
    end
    [~,ia,~]    = intersect(t,colh1,'stable');
    data1       = NaN(24,length(t)*4);
    for i=1:length(ia)
        data1(:,(ia(i)-1)*4+1:ia(i)*4) = data(:,(i-1)*4+1:i*4);
    end
    [~,ia,ib]   = intersect(t,Model.OutcomeVarN,'stable'); %Model.OutcomeVarN delivers pointer to data-set
end

%Load Results from Model structure - this code is the same as in
%PlotResults.m


for i=1:length(ia)
    if strcmp(Model.PlotType,'Cumulative') || strcmp(Model.PlotType,'DoubleCum');
       Gamma    = fliplr(Model.result(ib(i)).gc);
       GammaSTD = fliplr(Model.result(ib(i)).gcs);
    elseif strcmp(Model.PlotType,'Individual');
       Gamma    = fliplr(Model.result(ib(i)).g);
       GammaSTD = fliplr(Model.result(ib(i)).gs);
    else
        error('Unsupported PlotType');
    end

    switch Model.RespType
        case 'Macro'
            %rescale response to Percent
            Gamma = 100*Gamma;
            GammaSTD = 100*GammaSTD;
        case 'MacroVAR'
            %rescale response to Percent
            if (strcmp(OutcomeVarN(i),Model.VARLogTransList)'*ones(size(Model.VARLogTransList,1),1))==1 % transform Log vars to % changes
                Gamma = 100*Gamma;
                GammaSTD = 100*GammaSTD;            
            end
    end

    data1(:,(ia(i)-1)*4+1) = Gamma(:,2);
    data1(:,(ia(i)-1)*4+2) = GammaSTD(:,2);
    data1(:,(ia(i)-1)*4+3) = Gamma(:,3);
    data1(:,(ia(i)-1)*4+4) = GammaSTD(:,3);
end


table.colh1  = t;
table.colh2  = colh2;
table.data   = data1;
table.rowh   = rowh;
    
    
return