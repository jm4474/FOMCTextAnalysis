% This function calculates the score of phat
% Output is of dimension (kx+J-1) x T_sub

function l = phat_Score(phat,phat_Derivatives,policy_indicator,T_sub,J,kx)

l = zeros(kx+J-1,T_sub);

%{
for t = 1:T_sub
    for j = 1:J
        l(:,t) = l(:,t)+policy_indicator(t,j).*phat_Derivatives{t,j}./phat(t,j);
    end
end
%}
for t = 1:T_sub
    for j = 1:J
        if policy_indicator(t,j)==1
            l(:,t) = phat_Derivatives{t,j}./phat(t,j);
        end
    end
end

end