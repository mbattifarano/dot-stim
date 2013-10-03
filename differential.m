function d = differential(x,t)

if nargin == 1
    t = cumsum(ones(size(x)));
else
    dt=t;
end

d = diff(x)./dt;

try
    d = [d(1), d];
catch
    d = [d(1); d];
end

end