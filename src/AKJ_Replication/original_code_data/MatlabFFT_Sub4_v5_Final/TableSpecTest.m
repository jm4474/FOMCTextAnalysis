function TableSpecTest(pval,sig,Type)

if (~isempty(Type) && strcmp(Type,'FFT'))|| isempty(Type)

    dlmwrite('SpecTests.txt',[],'delimiter','');
    title1=['Specification Tests for ' ];
    title2=['Policy Model' char(9) 'CEE VAR' char([9 9]) 'CEE VAR'...
        char([9 9])  'PS1'  char([9 9])  'PS2' char([9 9])  'FFF'];
    title3=['Sample'  char(9)  '1959-2001' char([9 9]) '1989-2007'...
        char([9 9]) '1989-2007' char([9 9]) '1989-2007' char([9 9]) '1989-2001'];


    dlmwrite('SpecTests.txt',title1,'-append','delimiter','');
    dlmwrite('SpecTests.txt',title2,'-append','delimiter','');
    dlmwrite('SpecTests.txt',title3,'-append','delimiter','');


elseif (~isempty(Type) && strcmp(Type,'QE'))
    
    dlmwrite('SpecTestsQE.txt',[],'delimiter','');
    title1=['Specification Tests for ' ];
    title2=['Policy Model' char(9) 'Logit Aug08' char([9 9]) 'Logit Jan08 '...
        char([9 9])  'Logit Nov08'  char([9 9])  'LocProj Aug08'...
        char([9 9])  'LocProj Jan08' char([9 9])  'LocProj Nov08'];
    title3=['Sample'  char(9)  '2008-2012' char([9 9]) '2008-2012' char([9 9]) '2008-2012'...
        char([9 9]) '2008-2012' char([9 9]) '2008-2012' char([9 9]) '2008-2012'];


    dlmwrite('SpecTests.txt',title1,'-append','delimiter','');
    dlmwrite('SpecTests.txt',title2,'-append','delimiter','');
    dlmwrite('SpecTests.txt',title3,'-append','delimiter','');


end
for i = 1:size(pval,1)
    s = char(9);
    for j = 1:size(pval,2)
        if pval(i,j)<sig
            textstr = [num2str(pval(i,j)) char(9) '*' char(9)];
        else
            textstr = [num2str(pval(i,j)) char(9) ' ' char(9)];
        end
        s = [s textstr];
    end
    dlmwrite('SpecTests.txt',s,'-append','delimiter','');
end
    
    
return