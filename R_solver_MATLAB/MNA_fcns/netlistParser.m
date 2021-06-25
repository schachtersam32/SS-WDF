function [parsedNetlist,numNodes,numPorts,numEtc] = netlistParser(netlist)

[Name_, N1_, N2_, arg1_, arg2_, arg3_] = netlist{:};

numPorts = 0; numEtc = 0;
nlines = length(Name_);
% first deal with names
for i = 1:nlines
    n = char(Name_(i));
    if double(n(2)) == 167
        Name(i) = cellstr(n(3:end));
    else
        Name(i) = cellstr(n);
    end
end

for i = 1:nlines
   % use names to find numPorts, numNodes, numEtc
    if Name{i}(1) == 'V'
        numPorts = numPorts + 1;
    elseif Name{i}(1) == 'E'
        numEtc = numEtc + 1;
    end 
end

% Next, parse N1 and N2
for i = 1:nlines
    N1(i) = forceNodeDouble(N1_(i));
    N2(i) = forceNodeDouble(N2_(i));
end

numNodes = max([N1 N2]);
numNodes = numNodes(1); % in some cases numNodes can be a 2x1 array, this fixes that

% Lastly, deal with args
% arg1: Resistor value or VCVS port1
% arg2: VCVS port2
% arg3: VCVS gain
for i = 1:nlines
   arg1(i) = forceNodeDouble(arg1_(i));
   arg2(i) = forceNodeDouble(arg2_(i));
   arg3(i) = forceNodeDouble(arg3_(i));
end

parsedNetlist.Name = Name;
parsedNetlist.N1 = N1;
parsedNetlist.N2 = N2;
parsedNetlist.arg1 = arg1;
parsedNetlist.arg2 = arg2;
parsedNetlist.arg3 = arg3;


end