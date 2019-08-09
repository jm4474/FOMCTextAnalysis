function Jvalue=fn_value(y,X,ord_outcome,n_outcomes,n_sample,b_init)

aux_select = zeros(n_sample,n_outcomes);
for out_c = 1 : n_outcomes
    out = ord_outcome(out_c);
    aux_select(:,out_c) = y == out;
end

sum=0;
b_constant=b_init(1:n_outcomes-1);
b_covariates=b_init(n_outcomes:end);
for i = 1 : n_sample
    
    prob_out=zeros(n_outcomes,1);
    prob_out(1)=normcdf(b_constant(1)-X(i,:)*b_covariates);       
    if n_outcomes>2
        for out_c = 2 : n_outcomes-1
            prob_out(out_c)=normcdf(b_constant(out_c)-X(i,:)*b_covariates)...
                - normcdf(b_constant(out_c-1)-X(i,:)*b_covariates) ;       
        end
    end
    prob_out(n_outcomes)= 1 - normcdf(b_constant(n_outcomes-1)-X(i,:)*b_covariates);
    
    sum=sum+aux_select(i,:)*log(prob_out);   
end


Jvalue=-sum;
end