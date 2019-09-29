% This function calculate derivatives of P-score estimates
% Returns cell array of vectors indexed by {t,j}, each of dim (kx+J-1) x 1
% J-1 is the # of cut points

function phat_Derivatives = Oprob_derivatives(PScoreOutput)

X = PScoreOutput.X;
Cut_Points = PScoreOutput.Cut_Points;
Beta = PScoreOutput.Beta;

T_sub = size(X,1);
J = length(Cut_Points)+1;

for t = 1:T_sub
    phat_Derivatives{t,1} = -normpdf(Cut_Points(1)-X(t,:)*Beta)*X(t,:)';
    d1 = normpdf(Cut_Points(1)-X(t,:)*Beta);
    phat_Derivatives{t,1} = [phat_Derivatives{t,1};d1;zeros(J-2,1)];
    for j = 2:(J-1)
        phat_Derivatives{t,j} = (-normpdf(Cut_Points(j)-X(t,:)*Beta)+normpdf(Cut_Points(j-1)-X(t,:)*Beta))*X(t,:)';
        d1 = normpdf(Cut_Points(j)-X(t,:)*Beta);
        d0 = -normpdf(Cut_Points(j-1)-X(t,:)*Beta);
        phat_Derivatives{t,j} = [phat_Derivatives{t,j};zeros(j-2,1);d0;d1;zeros(J-j-1,1)];
    end
    phat_Derivatives{t,J} = normpdf(Cut_Points(J-1)-X(t,:)*Beta)*X(t,:)';
    d0 = -normpdf(Cut_Points(J-1)-X(t,:)*Beta);
    phat_Derivatives{t,J} = [phat_Derivatives{t,J};zeros(J-2,1);d0];
end

end
        