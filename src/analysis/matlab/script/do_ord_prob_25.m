types = ["simple_controls_yearly","simple_controls_quarterly","simple_controls",...
    "full_controls","full_controls_quarterly","full_controls_yearly"]
for i = 1:length(types)
    type = types(i)
    controls = readtable(type+"_ord_prob_p1.csv");
    change = readtable(type+"_ord_prob_p1_targets.csv");
    
    rng default
    
    x = controls{:,:};
    decision = change{:,:};
    
    d = ordinal(decision);
    
    [B,dev,stats] = mnrfit(x,d,'model','ordinal','link','probit');
    B;
    
    choices = [-.5,-.25,0,.25,.5];
    
    predic_prob = zeros(size(x,1),5);
    log_likelihood = zeros(size(x,1));
    
    for i_x= 1: size(x,1)
       predic_prob(i_x,:) = mnrval(B,x(i_x,:),'model','ordinal','link','probit');
       for i_d=1:5
           if choices(i_d) == decision(i_x,1)
               log_likelihood(i_x) = log(predic_prob(i_x,i_d));
           end
       end
    end
    
    dev;
    stats;
    sum(log_likelihood(:,1))
    
    %%
    
    aux = x*B(5:end);
    avg_response = mean(normpdf(B(4,1)+aux)-normpdf(B(3,1)+aux));
    result = avg_response*B(5:end,1);
    
    %%
    at_means_response = (normpdf(B(4,1)+mean(aux))-normpdf(B(3,1)+mean(aux)))*B(5:end,1)
    writematrix(predic_prob,'predicted_prob_'+type+'.csv');
end