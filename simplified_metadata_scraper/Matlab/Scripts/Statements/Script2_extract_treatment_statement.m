%% 

Tpepe = readtable('../../Output/Statements/Statements_text.csv');

%% Capture token before ' the target range for the federal funds rate at'

aux0 ...
      = regexp(Tpepe.statements,'(\w*) the target range for the federal funds rate at','tokens','once');

%% Capture token before 'its target' 

aux1 ...
      = regexp(Tpepe.statements,'(\w*)\sits target','tokens','once');
  
% (captures 82 out of 141 with one mistake)

%% Capture the token after 'decided to'

aux2 ...
      = regexp(Tpepe.statements,'decided today? to (\w*)','tokens','once');
  
%% Report the treatment 

ind0  = ~cellfun(@isempty,aux0);

aux1(ind0) ...
      = aux0(ind0);

ind1  = cellfun(@isempty,aux1);

Tpepe.treatment ...
      = aux1;
  
Tpepe.treatment(ind1) =  aux2(ind1); 

Tpepe.treatment(cellfun(@isempty,Tpepe.treatment))...
                      = {'empty'};
                  
Tpepe.treatment       = string(Tpepe.treatment);   

Tpepe.treatment(20)   = {'keep'};

%% Extract the treatment size basis points

aux3 ...
    = regexp(Tpepe.statements,'(\d{1,2})\sbasis points','tokens','once');

aux4 ...
    = regexp(Tpepe.statements,'(\d.\d)\spercentage point','tokens','once'); %only 2

aux3(cellfun(@isempty,aux3)) ...
    = aux4(cellfun(@isempty,aux3));

clear aux4

%% Treatment size

Tpepe.treatment_size ...
    = aux3;

aux4 ...
    = contains(Tpepe.treatment,'keep')|contains(Tpepe.treatment,'keeping')|...
      contains(Tpepe.treatment,'leave')|contains(Tpepe.treatment,'mantain');

Tpepe.treatment_size(aux4)={'0'};

%% Write table

writetable(Tpepe,'../../Output/Statements/CommentedFiles/Statements_text_treatment.csv')

%% NOTE: 

% There are 5 meetings that are not captured because they use the following
% expressions.

%decline in the federal funds rate of
%reduction in the federal funds rate of
%funds rate is expected to fall
%funds rate is expected to fall
%did not take action today to alter the stance of monetary policy