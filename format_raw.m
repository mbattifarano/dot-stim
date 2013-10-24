function fdata = format_raw(path_to_trial)
%FORMAT_RAW Summary of this function goes here
%   Detailed explanation goes here

raw = load([path_to_trial '/raw.mat']);

fdata.config=raw.config;
dt=1/double(fdata.config.refresh_rate);

trial=raw.trial;
for j=1:size(trial.dots,1)
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
end
fdata.trial=tmp_trial;

save([path_to_trial '/main.mat'],'fdata');
end

