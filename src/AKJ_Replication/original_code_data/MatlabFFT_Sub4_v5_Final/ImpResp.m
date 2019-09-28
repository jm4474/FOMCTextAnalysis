function C = ImpResp(Ac,R,d,p,h,ImpInd)

%compute impulse response

A  = [Ac(2:end,:)';[eye(d*(p-1)),zeros(d*(p-1),d)]];
E  = [eye(d);zeros(d*(p-1),d)];
C  = zeros(h,d);
Aj = eye(d*p,d*p);
for i = 1:h
    C((i-1)+1:i,:) = (E'*Aj*E*R*ImpInd)'; %multiply by ImpInd to extract ImpRes for policy shock
    Aj                 = A*Aj;    
end
return