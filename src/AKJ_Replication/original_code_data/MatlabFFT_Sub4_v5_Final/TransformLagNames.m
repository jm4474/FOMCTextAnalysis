function SpxL  = TransformLagNames(SpxLagList)

n    = size(SpxLagList,1);
SpxL = cell(n,1);

for i = 1:n
    SpxL(i,:) = cellstr([deblank(SpxLagList(i,:)),'(-1)']);
end
return