function import_stim_png( trials )
%IMPORT_STIM_PNG Summary of this function goes here
%   Detailed explanation goes here

trial_path='trials/';
png_path='png/';

if nargin == 0;
    trials=get_dir_contents(trial_path);
end

for i = 1:length(trials)
    disp(trials{i});
    png_dir = [trial_path trials{i} '/' png_path];
    png_files=get_dir_contents(png_dir);
    movie=[];
    for j = length(png_files):-1:1
        movie(:,:,:,j)=imread([png_dir '/' png_files{j}]);
    end
    movie = uint8(movie);
    save(['mat/' trials{i} '.mat'],'movie','-v7.3');
end
end

function out = get_dir_contents(path)
    tmp=dir(path);
    tmp={tmp.name};
    out=tmp(3:end);
end
