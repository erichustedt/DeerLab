function [err,data] = test(opt,olddata)

%=======================================
% Check Tikhonov regularization
%=======================================

Dimension = 200;
TimeStep = 0.008;
rmin = (4*TimeStep*52.04/0.85)^(1/3);
rmax = 6*(Dimension*TimeStep/2)^(1/3);
TimeAxis = linspace(0,TimeStep*Dimension,Dimension);
DistanceAxis = linspace(rmin,rmax,Dimension);
Distribution = gaussian(DistanceAxis,3,0.5);
Distribution = Distribution/sum(Distribution);

Kernel = getKernel(Dimension,TimeStep*1000);
Background = exp(-0.5*TimeAxis);

DipEvoFcn = Kernel*Distribution;

%Set optimal regularization parameter (found numerically lambda=0.13)
options = DAoptions('RegParam',0.13,'Solver','fnnls');
TikhResult1 = regularize(DipEvoFcn,Kernel,'tikhonov',options);
options.Solver = 'bppnnls';
TikhResult2 = regularize(DipEvoFcn,Kernel,'tikhonov',options);
options.Solver = 'lsqnonneg';
options.nonNegLSQsolTol = 1e-15;
TikhResult3 = regularize(DipEvoFcn,Kernel,'tikhonov',options);

err(1) = any(abs(TikhResult1 - Distribution)>1e-6);
err(2) = any(abs(TikhResult2 - Distribution)>1e-6);
err(3) = any(abs(TikhResult3 - Distribution)>1e-5);
err = any(err);
data = [];

if opt.Display
 	figure(8),clf
    hold on
    plot(DistanceAxis,Distribution,'k') 
    plot(DistanceAxis,TikhResult1,'r')
end

end