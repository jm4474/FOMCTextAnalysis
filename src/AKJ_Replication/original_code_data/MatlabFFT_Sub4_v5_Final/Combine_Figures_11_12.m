f  = figure;
subplot(2,1,1);
p1 = open('Macro_PcProbit_PSOct-2006_Dec-2008_HTOct-2006_Dec-2009FFED_Table_1.fig');
subplot(2,1,2);
p2 = open('YC_SummaryYC_PcProbit_PSOct-2006_Dec-2008_HTOct-2006_Dec-2009.fig');


saveas([p1,p2],'test.pdf');