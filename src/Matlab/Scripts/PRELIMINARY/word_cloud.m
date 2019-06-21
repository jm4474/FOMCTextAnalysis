ngram          = 2;

cleanTextData  = alternativeD;  

cleanDocuments = tokenizedDocument(cleanTextData);          % Tokenize

cleanDocuments = erasePunctuation(cleanDocuments);

listofstopwords = stopWords;

cleanDocuments  = removeWords(cleanDocuments, listofstopwords);

bngram             = bagOfNgrams(cleanDocuments, 'NgramLengths', ngram);      % Bag of ngrams

bow                = bagOfWords(cleanDocuments);

figure('Name', 'Alternative D')

wordcloud(bngram)