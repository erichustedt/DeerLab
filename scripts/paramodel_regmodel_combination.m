%================================================================
% DeerAnalyis2
% Example: Paramteric mode fitting & regularization combination
% Perform simultaneous parametric model fitting of the background 
% and Tikhonov regularization for a one-step analysis of the data
%================================================================

clear,clc,clf

%Preparation
%----------------------------------------------
t = linspace(-0.2,4,250);
r = time2dist(t);
dr = mean(diff(r));
P = rd_twogaussian(r,[5 0.6 4 0.4 0.6]) + rd_twogaussian(r,[5.5 0.4 4.5 0.4 0.2]);
P =  P/sum(P)/dr;
trueparam = [0.3 0.15];

%Construct exponential background
B = td_exp(t,trueparam(2));

%Generate signal
V = dipolarsignal(t,r,P,'ModDepth',trueparam(1),'Background',B,'Noiselevel',0.01);

%Fitting
%----------------------------------------------

%Create function handle depending on r and param from the custom model 
fcnhandle = @(t,param) mymodel(t,param,r,V);

%Initial guess
param0 = [0.4,0.2];

%Launch the fitting of the B-parametric model + Tikhonov regularization
parafit = fitparamodel(V,fcnhandle,t,param0,'Lower',[0 0],'Upper',[1 10],'TolFun',1e-3);

%Obtain the fitted signal and distance distribution
[Vfit,Pfit] = mymodel(t,parafit,r,V);


%Plot results
%----------------------------------------------
subplot(121)
plot(r,P,'k',r,Pfit,'b','LineWidth',1.5)
box on, grid on, axis tight
xlabel('Distance [nm]')
ylabel('P(r)')

subplot(122)
plot(t,V,'k',t,Vfit,'b','LineWidth',1.5)
xlabel('Time [\mus]')
ylabel('V(t)')
title(sprintf('\\lambda = %.2f/%.2f  k = %.3f/%.3f',...
        parafit(1),trueparam(1),parafit(2),trueparam(2)))
box on, grid on, axis tight

    
%Definition of the custom model
%----------------------------------------------

function [Vfit,Pfit] = mymodel(t,param,r,V)
    
    %Fit the modulation depth as first parameter...
    lambda = param(1);
    k = param(2);
    
    %... and the decay rate of the background as second parameter
    Bfit = td_exp(t,k);
    %Construct a kernel with the fitted background
    KB = dipolarkernel(t,r,lambda,sqrt(Bfit));
    %Regularize the data using the fitted backgorund
    Pfit = fitregmodel(V./sqrt(Bfit),KB,r,'tikhonov',0.45);
    %Get the signal for comparison in time-domain
    KB = dipolarkernel(t,r,lambda,Bfit);
    Vfit = KB*Pfit; 
    plot(t,V,'.',t,Vfit),drawnow
end
