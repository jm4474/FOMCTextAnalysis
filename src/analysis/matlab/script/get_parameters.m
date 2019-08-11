function b_opt = get_parameters(y,X)

ord_outcome = sort( unique(y));
n_outcomes = length(ord_outcome);
n_sample=length(y);
b_init = (1:n_outcomes-1)./n_outcomes;
b_init = [b_init, ones(1, size(X,2))]';

% Compute the likelihood
options = optimset('TolX',1e-8);
b_opt=fminsearch(@(x)fn_value(y,X,ord_outcome,n_outcomes,n_sample,x), b_init,options);

end