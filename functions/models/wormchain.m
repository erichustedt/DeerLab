function output = wormchain(r,param)
%
% Worm-like chain model near the rigid limit
% name    symbol default lower bound upper bound
% par(1)  L      3.7     1.5         10             length of the worm-like chain
% par(2)  Lp     10      2           100            persistence length
%

nParam = 2;

if nargin==0
    %If no inputs given, return info about the parametric model
    info.Model  = 'Worm-like chain model near rigid limit';
    info.Equation  = '';
    info.nParam  = nParam;
    info.parameters(1).name = 'Chain length';
    info.parameters(1).range = [1.5 10];
    info.parameters(1).default = 3.7;
    info.parameters(1).units = 'nm';
    
    info.parameters(2).name = 'Persistence length';
    info.parameters(2).range = [2 100];
    info.parameters(2).default = 10;
    info.parameters(2).units = 'nm';
    
    output = info;
    
elseif nargin == 2
    
    %If user passes them, check that the number of parameters matches the model
    if length(param)~=nParam
        error('The number of input parameters does not match the number of model parameters.')
    end
    
    %Prepare parameters
    L=param(1);
    Lp=param(2);
    kappa=Lp/L;
    
    %Get normalized distance axis
    normDistAxis=r/L;
    Distribution=zeros(size(r));
    crit=kappa*(1 - normDistAxis);
    %Compute ditribution using two terms of the expansion
    rcrit = normDistAxis(crit>0.2);
    Distribution(crit>0.2)=2*kappa/(4*pi)*(pi^2*(-1)^(2)*exp(-kappa*pi^2*(1-rcrit)) ...
        + pi^2*4*(-1)^(3)*exp(-kappa*pi^2*4*(1-rcrit)));
    rcrit = normDistAxis(crit>0);
    Distribution(crit>0) = kappa/(4*pi*2*sqrt(pi))*(1./(kappa*(1 - rcrit)).^(3/2).*exp(-(1 - 1/2)^2./(kappa*(1 - rcrit))).*(4.*((1 - 1/2)./sqrt(kappa*(1-rcrit))).^2-2) ...
        + 1./(kappa*(1 - rcrit)).^(3/2).*exp(-(2 - 1/2)^2./(kappa*(1 - rcrit))).*(4.*((2 - 1/2)./sqrt(kappa*(1-rcrit))).^2-2));
    
    %Normalize integral
    Distribution = Distribution/sum(Distribution);
    output = Distribution;
    
else
    
    %Else, the user has given wrong number of inputs
    error('Model requires two input arguments.')
end

return