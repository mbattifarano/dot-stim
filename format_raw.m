function fdata = format_raw(path_to_trial)
%FORMAT_RAW Summary of this function goes here
%   Detailed explanation goes here

raw = load([path_to_trial '/raw.mat']);

fdata.config=raw.config;
dt=1/double(fdata.config.refresh_rate);

trial=raw.trial;
fprintf('MATLAB: Converting data...\n');
for j=size(trial.dots,1):-1:1
    x=double(trial.dots(j,:,1))+double(fdata.config.field_shift(1));
    y=double(trial.dots(j,:,2))+double(fdata.config.field_shift(2));
    dx=differential(x,dt);
    dy=differential(y,dt);
    tmp_trial(j)=struct('x',x',...
        'y',y',...
        'dx',dx',...
        'dy',dy',...
        'noise',trial.noise(j,:)',...
        'diode',trial.diode(j)',...
        'time',dt*(j-1));
    fprintf('Finished tmp_trial(%d)\n',j);
end
fdata.trial=tmp_trial;
fprintf('MATLAB: Saving main.mat...\n');
save([path_to_trial '/main.mat'],'fdata');
fprintf('MATLAB: Leaving format_raw.m\n');
end

