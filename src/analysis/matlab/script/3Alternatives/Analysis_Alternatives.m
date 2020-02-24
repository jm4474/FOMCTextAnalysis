%% Data Preparation

[NUM,TXT,RAW] ...
    = xlsread('alternative_outcomes_and_corpus.xlsx'); 
      %I was not able to load the csv file directly, I had to copy-paste 
      %into a new file and save as .xlsx
                
dates ...
    = datetime(NUM(:,2),'ConvertFrom','Excel','format','MM/dd/yyyy');
      %Dates in Matlab Format
      
AltA ...
    = TXT(2:end,2); 

AltB ...
    = TXT(2:end,4);

AltC ...
    = TXT(2:end,6);


TargetA ...
    = NUM(:,4);

TargetB ...
    = NUM(:,6);

TargetC ...
    = NUM(:,8);

Decision ...
    = NUM(:,11);

%% Plot Targets under each alternative

%Period 88-2001 
%It seems that over this period A<B=0<C. 

figure()

plot(dates(1:76),TargetA(1:76),'vb'); hold on

plot(dates(1:76),TargetB(1:76),'or'); hold on

plot(dates(1:76),TargetC(1:76),'^g'); hold off


ylim([-1,1])

title('Alternatives: 1988-2001')

legend('A','B','C')

legend boxoff

print(gcf,'-depsc2','1Figures/Alternatives_88_01')

%% Bag of Words under Each Alternative 1998-2001

textAltA ...
    = string(AltA(1:76));

textAltB ...
    = string(AltB(1:76));

textAltC ...
    = string(AltC(1:76));

ngram ...
    = 1;

mystopwords = {'interest rates','rate','federal funds'...
               'rates','alternatives','market','might',...
               'alternative','committee','funds','percent',...
               'interest','market','markets','term',...
               'federal','a','â','b','c','s','12' ...
               'inflation','policy','growth','likely'};

addpath('2Functions');           
           
bowA...
   = mybag(textAltA,ngram,mystopwords);

figure()

wordcloud(bowA) 

print(gcf,'-depsc2','1Figures/WordCloudA_88_01')


bowB...
   = mybag(textAltB,ngram,mystopwords);

figure()

wordcloud(bowB) 

print(gcf,'-depsc2','1Figures/WordCloudB_88_01')

bowC...
   = mybag(textAltC,ngram,mystopwords);

figure()

wordcloud(bowC) 

print(gcf,'-depsc2','1Figures/WordCloudC_88_01')

%%

%Period 2002-2004

figure()

plot(dates(77:100),TargetA(77:100),'vb'); hold on

plot(dates(77:100),TargetB(77:100),'or'); hold on

plot(dates(77   :100),TargetC(77:100),'^g'); hold on


ylim([-1,1])

title('Alternatives: 2002-2004')

legend('A','B','C')

legend boxoff







