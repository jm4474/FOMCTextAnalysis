function [bow] = mybag(textData,ngram,mystopwords)
% This function generates a bag of words
% To do: Write documentation
% February 2020

cleanTextData ...
    = lower(textData);                           % Lower case

cleanDocuments ...
    = tokenizedDocument(cleanTextData);          % Tokenize

cleanDocuments ...
    = erasePunctuation(cleanDocuments);          % Erase punctuation

listofstopwords ...
    = [stopWords, mystopwords];      %stopwords is the matlab default

cleanDocuments  ...
    = removeWords(cleanDocuments, listofstopwords);

bow ...
    = bagOfNgrams(cleanDocuments,'NgramLengths', ngram);              
      % Frequency of Words from Tokenized, cleaned documents

%bow             = removeInfrequentWords(bow,19);           % Remove words that appear 19 times or less in the bag of words 


end

