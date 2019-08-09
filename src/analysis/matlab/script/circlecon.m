function [c,ceq] = circlecon(b_init)
global n_sample n_outcomes X D
b_constant=b_init(1:n_outcomes-1);
b_covariates=b_init(n_outcomes:end);

phat=zeros(n_sample,n_outcomes);
for i = 1 : n_sample
    phat(i,1) = normcdf(b_constant(1) - X(i,:) * b_covariates);       
    if n_outcomes>2
        for out_c = 2 : n_outcomes-1
            phat(i,out_c) = normcdf(b_constant(out_c) - X(i,:) * b_covariates)...
                - normcdf(b_constant(out_c-1) - X(i,:) * b_covariates) ;       
        end
    end
    phat(i,n_outcomes) = 1 - normcdf(b_constant(n_outcomes-1) - X(i,:) * b_covariates);
end

aux_weight=D./phat;
weights=zeros(n_outcomes,1);
basecat_c=3;
for out=1:n_outcomes
    weights(out)=sum(aux_weight(:,out))-sum(aux_weight(:,basecat_c));
end
c = [];
ceq = weights;
end
