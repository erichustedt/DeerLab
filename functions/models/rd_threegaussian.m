function output = rd_threegaussian(r,param)
%
% THREEGAUSSIAN Sum of three Gaussian distributions parametric model
%
%   info = THREEGAUSSIAN
%   Returns an (info) structure containing the specifics of the model.
%
%   P = THREEGAUSSIAN(r,param)
%   Computes the N-point model (P) from the N-point distance axis (r) according to 
%   the paramteres array (param). The required parameters can also be found 
%   in the (info) structure.
%
% PARAMETERS
% name      symbol default lower bound upper bound
% --------------------------------------------------------------------------
% param(1)  <r1>   2.5     1.5         20         1st mean distance
% param(2)  s(r1)  0.5     0.05        5          std. dev. of 1st distance
% param(3)  <r2>   3.5     1.5         20         2nd mean distance
% param(4)  s(r2)  0.5     0.05        5          std. dev. of 2nd distance
% param(5)  <r3>   5.0     1.5         20         3rd mean distance
% param(6)  s(r3)  0.5     0.05        5          std. dev. of 3rd distance
% param(7)  p1     0.3     0           1          fraction of pairs at 1st distance
% param(8)  p2     0.3     0           1          fraction of pairs at 2nd distance
% --------------------------------------------------------------------------
%
% Copyright(C) 2019  Luis Fabregas, DeerAnalysis2
%
% This program is free software: you can redistribute it and/or modify
% it under the terms of the GNU General Public License 3.0 as published by
% the Free Software Foundation.

nParam = 8;

if nargin==0
    %If no inputs given, return info about the parametric model
    info.Model  = 'Three-Gaussian distribution';
    info.Equation  = ['A1*exp(-(r-<r1>)�/(',char(963),'1*sqrt(2))�) + A2*exp(-(r-<r2>)�/(',char(963),'2*sqrt(2))�) + (1-A1-A2)*exp(-(r-<r3>)�/(',char(963),'3*sqrt(2))�)'];
    info.nParam  = nParam;
    info.parameters(1).name = 'Mean distance <r1> 1st Gaussian';
    info.parameters(1).range = [1 20];
    info.parameters(1).default = 2.5;
    info.parameters(1).units = 'nm';
    
    info.parameters(2).name = ['Standard deviation ',char(963),'1 1st Gaussian'];
    info.parameters(2).range = [0.05 5];
    info.parameters(2).default = 0.5;
    info.parameters(2).units = 'nm';
    
    info.parameters(3).name = 'Mean distance <r2> 2nd Gaussian';
    info.parameters(3).range = [1 20];
    info.parameters(3).default = 3.5;
    info.parameters(3).units = 'nm';
    
    info.parameters(4).name = ['Standard deviation ',char(963),'2 2nd Gaussian'];
    info.parameters(4).range = [0.05 5];
    info.parameters(4).default = 0.5;
    info.parameters(4).units = 'nm';
    
    info.parameters(5).name = 'Mean distance <r3> 3rd Gaussian';
    info.parameters(5).range = [1 20];
    info.parameters(5).default = 3.5;
    info.parameters(5).units = 'nm';
    
    info.parameters(6).name = ['Standard deviation ',char(963),'3 3rd Gaussian'];
    info.parameters(6).range = [0.05 5];
    info.parameters(6).default = 0.5;
    info.parameters(6).units = 'nm';
    
    info.parameters(7).name = 'Relative amplitude A1 1st Gaussian';
    info.parameters(7).range = [0 1];
    info.parameters(7).default = 0.3;
    
    info.parameters(8).name = 'Relative amplitude A2 2nd Gaussian';
    info.parameters(8).range = [0 1];
    info.parameters(8).default = 0.3;
       
    output = info;
    
elseif nargin == 2
    
    %If user passes them, check that the number of parameters matches the model
    if length(param)~=nParam
        error('The number of input parameters does not match the number of model parameters.')
    end
    
    %If necessary inputs given, compute the model distance distribution
    Gaussian1 = exp(-((r-param(1))/(param(2))).^2);
    Gaussian2 = exp(-((r-param(3))/(param(4))).^2);
    Gaussian3 = exp(-((r-param(5))/(param(6))).^2);
    Distribution = param(7)*Gaussian1 + param(8)*Gaussian2 + max(1 - param(5) - param(8),0)*Gaussian3;
    if ~iscolumn(Distribution)
        Distribution = Distribution';
    end
    %Normalize
    Distribution = Distribution/sum(Distribution)/mean(diff(r));
    output = Distribution;
else
    %Else, the user has given wrong number of inputs
    error('Model requires two input arguments.')
end

return