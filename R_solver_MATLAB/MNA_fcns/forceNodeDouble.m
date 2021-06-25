function N = forceNodeDouble(N_)
    n = char(N_);
    if contains(n,'N')
        N = str2double(n(2:end));
    else
        N = str2double(n);
    end
end