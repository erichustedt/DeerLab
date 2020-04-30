%
% FITSIGNAL  Fit model to dipolar time-domain trace
%
%   [Vfit,Pfit,Bfit,parfit,parci,stats] = FITSIGNAL(V,t,r,dd,bg,ex,par0)
%   __ = FITSIGNAL(V,t,r,dd,bg,ex)
%   __ = FITSIGNAL(V,t,r,dd,bg)
%   __ = FITSIGNAL(V,t,r,dd)
%   __ = FITSIGNAL(V,t,r)
%   __ = FITSIGNAL({V1,V2,__},{t1,t2,__},r,dd,{bg1,bg2,__},{ex1,ex2,__})
%   __ = FITSIGNAL({V1,V2,__},{t1,t2,__},r,dd,{bg1,bg2,__},ex)
%   __ = FITSIGNAL({V1,V2,__},{t1,t2,__},r,dd)
%   __ = FITSIGNAL({V1,V2,__},{t1,t2,__},r)
%
%   Fits a dipolar model to the experimental signal in V, using distance axis r.
%   The model is specified by the distance distribution (dd), the background
%   (bg), and the experiment (ex). If multiple signals (V1,V2,...) and their
%   corresponding time axes (t1,t2,...) are given, they will be fitted globally
%   to the specified distance distribution (dd). For each signal a specific
%   background (bg1,bg2,...) and experiment (ex1,ex2) models can be assigned.
%
%   FITSIGNAL can handle both parametric and non-parametric distance
%   distribution models.
%
%  Input:
%    V      time-domain signal to fit (N-element vector)
%    t      time axis, in microseconds (N-element vector)
%    r      distance axis, in nanometers (M-element vector)
%    dd     distance distribution model (default 'P')
%           - function handle to parametric distribution model
%           - 'P' to indicate parameter-free distribution (default)
%           - 'none' to indicate no distribution, i.e. only background
%    bg     background model (default @bg_exp)
%           - function handle to parametric background model
%           - 'none' to indicate no background decay
%    ex     experiment model (default @ex_4pdeer)
%           - function handle to experiment model
%           - 'none' to indicate simple dipolar oscillation (mod.depth = 1)
%    par0   starting parameters, 3-element cell array {par0_dd,par0_bd,par0_ex}
%           default: {[],[],[]} (automatic choice)
%
%  Output:
%    Vfit   fitted time-domain signal
%    Pfit   fitted distance distribution
%    Bfit   fitted background decay
%    parfit structure with fitted parameters
%           .dd  fitted parameters for distance distribution model
%           .bg  fitted parameters for background model
%           .ex  fitted parameters for experiment model
%    parci structure with confidence intervals for parameter, similar to parfit
%    stats goodness of fit statistical estimators, N-element structure array

% Example:
%    Vfit = fitsignal(Vexp,t,r,@dd_gauss,@bg_exp,@ex_4pdeer)
%

% This file is a part of DeerLab. License is MIT (see LICENSE.md).
% Copyright(c) 2019-2020: Luis Fabregas, Stefan Stoll and other contributors.

function [Vfit,Pfit,Bfit,parfit,parci,stats] = fitsignal(Vexp,t,r,dd_model,bg_model,ex_model,par0)

if nargin<3
    error('At least three inputs (V,t,r) must be specified.');
end

% Validation of Vexp, t, r
%-------------------------------------------------------------------------------
if ~iscell(Vexp)
    Vexp = {Vexp};
end
nSignals = numel(Vexp);
if ~iscell(t)
    t = {t};
end
if numel(t) ~= nSignals
    error('The same number of signals V and time axes must be provided.')
end
for i = 1:nSignals
    Vexp{i} = Vexp{i}(:);
    t{i} = t{i}(:);
    if length(Vexp{i})~=length(t{i})
        error('V{%i} and t{%i} must have the same number of elements.',i,i)
    end
    if ~isreal(Vexp{i})
        error('Input signals cannot be complex-valued.')
    end
    validateattributes(Vexp{i},{'numeric'},{'vector'},mfilename,'V (1st input)');
    validateattributes(t{i},{'numeric'},{'vector'},mfilename,'t (2nd input)');
end
validateattributes(r,{'numeric'},{'vector'},mfilename,'r (3rd input)');

% Regularization settings
regtype = 'tikh';
regparam = 'aic';
alphaOptThreshold = 1e-3; % relative parameter change threshold for reoptimizing alpha


% Set defaults
if nargin<4, dd_model = 'P'; end
if nargin<5, bg_model = @bg_hom3d; end
if nargin<6, ex_model = @ex_4pdeer; end
if nargin<7, par0 = {[],[],[]}; end

calculateCI = nargout>=5 || nargout==0;

if ~isempty(par0)
    if ~iscell(par0) || numel(par0)~=3
        error('Initial parameters (7th input) must be a 3-element cell array.')
    end
end

% Get information about distance distribution parameters
%-------------------------------------------------------------------------------
par0_dd = [];
lower_dd = [];
upper_dd = [];
N_dd = 0;
includeForeground = true;
if isa(dd_model,'function_handle')
    [par0_dd,lower_dd,upper_dd,N_dd] = getmodelparams(dd_model);
    parfreeDistribution = false;
elseif ischar(dd_model) && strcmp(dd_model,'P')
    parfreeDistribution = true;
elseif ischar(dd_model) && strcmp(dd_model,'none')
    includeForeground = false;
    parfreeDistribution = false;
else
    error('Distribution model (4th input) must either be a function handle, ''P'', or ''none''.')
end

% Get information about background parameters
%-------------------------------------------------------------------------------
par0_bg = cell(1,nSignals);
lower_bg = cell(1,nSignals);
upper_bg = cell(1,nSignals);
N_bg = zeros(nSignals,1);
if ~iscell(bg_model)
    bg_model = {bg_model};
end
if numel(bg_model)~=nSignals
    bg_model = repmat(bg_model,nSignals,1);
end
includeBackground = NaN(nSignals,1);
for i = 1:nSignals
    includeBackground(i) = true;
    if isa(bg_model{i},'function_handle')
        [par0_bg{i},lower_bg{i},upper_bg{i},N_bg(i)] = getmodelparams(bg_model{i});
    elseif ischar(bg_model{i}) && strcmp(bg_model{i},'none')
        includeBackground(i) = false;
    else
        error('Background model (5th input) must either be a function handle, or ''none''.')
    end
end

% Get information about experiment parameters
%-------------------------------------------------------------------------------
par0_ex = cell(1,nSignals);
lower_ex = cell(1,nSignals);
upper_ex = cell(1,nSignals);
N_ex = zeros(nSignals,1);
if ~iscell(ex_model)
    ex_model = {ex_model};
end
if numel(ex_model)~=nSignals
    ex_model = repmat(ex_model,nSignals,1);
end
includeExperiment = NaN(nSignals,1);
for i = 1:nSignals
    includeExperiment(i) = true;
    if isa(ex_model{i},'function_handle')
        [par0_ex{i},lower_ex{i},upper_ex{i},N_ex(i)] = getmodelparams(ex_model{i},t{i});
    elseif ischar(ex_model{i}) && strcmp(ex_model{i},'none')
        includeExperiment(i) = false;
    else
        error('Experiment models must either be a function handle, or ''none''.')
    end
end

% Catch nonsensical situation
if any(~includeForeground & ~includeBackground)
    error('Cannot fit anything without distribution model and without background model.')
end

% Combine all parameters into a single vector
if isempty(par0{1}), par0{1} = par0_dd; end
if isempty(par0{2}), par0{2} = par0_bg; end
if isempty(par0{3}), par0{3} = par0_ex; end
par0 = [par0{1} cell2mat(par0{2}) cell2mat(par0{3})];
lower = [lower_dd cell2mat(lower_bg) cell2mat(lower_ex)];
upper = [upper_dd cell2mat(upper_bg) cell2mat(upper_ex)];
nParams = numel(par0);

% Build index vectors for accessing parameter subsets
ddidx = 1:N_dd;
bgidx = cell(nSignals,1);
exidx = cell(nSignals,1);
for i = 1:nSignals
    bgidx{i} = N_dd + sum(N_bg(1:i-1)) + (1:N_bg(i));
    exidx{i} = N_dd + sum(N_bg) + sum(N_ex(1:i-1)) + (1:N_ex(i));
end

% Perform fitting
%-------------------------------------------------------------------------------
RegularizationOnly = nParams==0;
if RegularizationOnly
    
    % Solve regularization only
    for i = 1:nSignals
        K{i} = dipolarkernel(t{i},r); 
    end
    Pfit = fitregmodel(Vexp,K,r,regtype,regparam);    
    for i = 1:nSignals
        Vfit{i} = K{i}*Pfit;
        Bfit{i} = ones(size(Vexp{i}));
    end
    parfit_ = [];
    parci_ = [];
    
else
    
    % Keep track of alpha and parameter vector across iterations, to avoid
    % doing alpha optimizations if parameter vector doesn't change much
    par_prev = [];
    regparam_prev = [];
    
    % Create some containers to cache variables not changing between
    % different signals in global fitting
    P_cached = [];
    K_cached = [];
    B_cached = [];
    
    % Fit the parameters
    args = {Vexp,@Vmodel,t,par0,'Lower',lower,'Upper',upper,'TolFun',1e-5};
    if calculateCI
        [parfit_,~,parci_] = fitparamodel(args{:});
    else
        parfit_ = fitparamodel(args{:});
        parci_ = [];
    end
    
    % Calculate the fitted signal, background, and distribution
    alpha = regparam; % use original setting for final run
    for i = 1:nSignals
        [Vfit{i},Bfit{i},Pfit] = Vmodel([],parfit_,i);
    end
end

% Return fitted parameters and confidence intervals in structures
%-------------------------------------------------------------------------------
parfit_ = parfit_(:);
parfit.dd = parfit_(ddidx);
for i = 1:nSignals
    parfit.bg{i} = parfit_(bgidx{i});
    parfit.ex{i} = parfit_(exidx{i});
end
if calculateCI
    parci.dd = parci_(ddidx,:);
    for i = 1:nSignals
        parci.bg{i} = parci_(bgidx{i},:);
        parci.ex{i} = parci_(exidx{i},:);
    end
end

% Plotting
%-------------------------------------------------------------------------------
if nargout==0
    for i = 1:nSignals
        subplot(2,nSignals,i);
        plot(t{i},Vexp{i},t{i},Vfit{i})
        axis tight
        grid on
        xlabel('time (us)');
        ylabel(sprintf('V\\{%d\\}',i));
        legend('exp','fit');
    end
    subplot(2,1,2);
    plot(r,Pfit);
    xlabel('distance (nm)');
    axis tight
    ylabel('P (nm^{-1})');
    grid on
    drawnow
    
    disp('Fitted parameters and confidence intervals')
    str = '  %s{%d}(%d):   %10f  (%10f, %10f)  %s (%s)\n';
    if numel(parfit.dd)>0
        pars = dd_model().parameters;
        for p = 1:numel(parfit.dd)
            c = parfit.dd(p);
            ci = parci.dd(p,:)-c;
            fprintf(str,'dd',1,p,c,...
                ci(1),ci(2),pars(p).name,pars(p).units);
        end
    end
    if numel(parfit.bg)>0
        for i = 1:nSignals
            pars = bg_model{i}().parameters;
            for p = 1:numel(parfit.bg{i})
                c = parfit.bg{i}(p);
                ci = parci.bg{i}(p,:)-c;
                fprintf(str,'bg',i,p,c,...
                    ci(1),ci(2),pars(p).name,pars(p).units)
            end
        end
    end
    if numel(parfit.ex)>0
        for i = 1:nSignals
            pars = ex_model{i}(t).parameters;
            for p = 1:numel(parfit.ex{i})
                c = parfit.ex{i}(p);
                ci = parci.ex{i}(p,:)-c;
                fprintf(str,'ex',i,p,c,...
                    ci(1),ci(2),pars(p).name,pars(p).units)
            end
        end
    end
end

% Return numeric and not cell arrays if there is only one signal
if nSignals==1
    Vfit = Vfit{1};
    Bfit = Bfit{1};
    if ~isempty(parci_)
        parci.bg = parci.bg{1};
        parci.ex = parci.ex{1};
    end
end

%===============================================================================

% General multi-pathway DEER signal model function
    function [V,B,P] = Vmodel(~,par,idx)
        
        % Calculate all K, all B, and P when called for first signal
        if idx==1
            for j = 1:nSignals
                % Calculate the background and the experiment kernel matrix
                if includeExperiment(j)
                    pathinfo = ex_model{j}(t{j},par(exidx{j}));
                    if includeBackground(j)
                        Bfcn = @(t,lam) bg_model{j}(t,par(bgidx{j}),lam);
                        B{j} = dipolarbackground(t{j},pathinfo,Bfcn);
                    else
                        Bfcn = [];
                        B{j} = ones(numel(t{j}),1);
                    end
                    K{j} = dipolarkernel(t{j},r,pathinfo,Bfcn);
                else
                    K{j} = dipolarkernel(t{j},r);
                    if includeBackground(j)
                        Bfcn = @(t) bg_model{j}(t,par(bgidx{j}));
                        B{j} = Bfcn(t{j});
                    else
                        B{j} = ones(numel(t{j}),1);
                    end
                end
            end
            % Get the distance distribution
            if includeForeground && nargin<4
                
                % Use the alpha-search settings by default
                alpha = regparam;
                % If the parameter vectors has not changed by much...
                if ~isempty(par_prev)
                    if all(abs(par_prev-par)./par < alphaOptThreshold)
                        % ...use the alpha optimized in the previous iteration
                        alpha = regparam_prev;
                    end
                end
                par_prev = par;
                
                if parfreeDistribution
                    [P,~,regparam_prev] = fitregmodel(Vexp,K,r,regtype,alpha);
                else
                    P = dd_model(r,par(ddidx));
                end
            else
                P = zeros(numel(t),1);
            end
            K_cached = K;
            B_cached = B;
            P_cached = P;
        else
            % Compute the rest of the signals from the cached results
            K = K_cached;
            B = B_cached;
            P = P_cached;
        end
        
        % Compute the total signal
        if includeForeground
            V = K{idx}*P;
        else
            V = B{idx};
        end
        B = B{idx};
        
    end

end

function [par0,lo,up,N] = getmodelparams(model,t)

if contains(func2str(model),'ex_')
    info = model(t);
else
    info = model();
end
par0 = [info.parameters.default];
range = [info.parameters.range];
lo = range(1:2:end-1);
up = range(2:2:end);
N = numel(par0);

end
