function avgmargfx = get_marginal(X,y,b_opt,selector_outcome)
    ord_outcome = unique(y);
    n_outcomes = length(ord_outcome);
    n_sample=length(y);
    aux_sum=zeros(n_outcomes,1);
    b_constant=b_opt(1:n_outcomes-1);
    b_covariates=b_opt(n_outcomes:end);
    b_marginal=b_covariates(selector_outcome);
    for i = 1 : n_sample
        marginal_out=zeros(n_outcomes,1);
        marginal_out(1)=-b_marginal*normpdf(b_constant(1)-X(i,:)*b_covariates);       
        if n_outcomes>2
            for out_c = 2 : n_outcomes-1
                marginal_out(out_c)=-b_marginal*(normpdf(b_constant(out_c)-X(i,:)*b_covariates)...
                    - normpdf(b_constant(out_c-1)-X(i,:)*b_covariates)) ;       
            end
        end
        marginal_out(n_outcomes)= b_marginal*normpdf(b_constant(n_outcomes-1)-X(i,:)*b_covariates);

        aux_sum=aux_sum+marginal_out;  
    end

    avgmargfx=1/n_sample* aux_sum;
end