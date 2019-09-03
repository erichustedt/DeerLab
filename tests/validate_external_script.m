function [err,data,maxerr] = test(opt,olddata)

t = linspace(0,4,200);
r = time2dist(t);


Parameters(1).name = 'regparam';
Parameters(1).values = linspace(0.1,1,5);

Parameters(2).name = 'validationnoise';
Parameters(2).values = linspace(0.01,0.1,2);



if opt.Display
    f = figure(1); clf;AxisHandle = axes(f);
else
    AxisHandle = [];
end

[meanOut,stdOut] = validate('Pfit',Parameters,'./data/validationscript_test.m','AxisHandle',AxisHandle);

err = false;
data = [];
maxerr = -3;

if opt.Display
        cla
        hold on
        plot(r,meanOut,'b','LineWidth',1)
        f = fill([r fliplr(r)] ,[meanOut.'+stdOut.' fliplr(meanOut.'-stdOut.')],...
            'b','LineStyle','none');
        f.FaceAlpha = 0.5;
        hold('off')
        axis('tight')
        grid('on')
        box('on')
end

end