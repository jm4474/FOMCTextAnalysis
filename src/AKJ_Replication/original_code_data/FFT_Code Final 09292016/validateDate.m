%This function checks if the input date strings are:
%1. of 1d string array, and
%2. of correct format, and
%3. of strictly ascending order

function output = validateDate(date_string)

output = 1;

% Check if input is column vector
% This requires input is array of strings other than character array
if size(date_string,1) ~= 1 && size(date_string,2) ~= 1
    output = 0;
end

% Check if date format is correct
try
    date_num = datenum(date_string);
catch
    output = 0;
end

% Check if dates are of strictly ascending order
if output == 1 && ~issorted(date_num) && length(unique(date_num)) ~= size(date_num,1)
    output = 0;
end

end