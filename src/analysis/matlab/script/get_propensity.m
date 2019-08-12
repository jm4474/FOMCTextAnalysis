function phat = get_propensity(X,y,b_opt)

ord_outcome = unique(y);
n_outcomes = length(ord_outcome);
n_sample=length(y);

b_constant=b_opt(1:n_outcomes-1);
b_covariates=b_opt(n_outcomes:end);

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

end