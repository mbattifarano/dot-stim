%%
path ='trials/';
contents=dir(path);
trial_names={contents.name};
trial_names=trial_names(3:end);

for i=1:length(trial_names);
    trialname=trial_names{i};
    disp(trialname)
    
    load([path trialname '/' trialname '.mat']);
    dot_pos=squeeze(dot_pos);
    nframes=size(dot_pos,1);
    optic_flow = zeros(768,1024,2,nframes-1);
    
    if dfns.ndots == 1
        x_prev=squeeze(dot_pos(1,1));
        y_prev=squeeze(dot_pos(1,2));
    else
        x_prev=squeeze(dot_pos(1,:,1));
        y_prev=squeeze(dot_pos(1,:,2));
    end
    
        
    for j=2:nframes
        if dfns.ndots == 1
            x_now=squeeze(dot_pos(j,1));
            y_now=squeeze(dot_pos(j,2));
        else
            x_now=squeeze(dot_pos(j,:,1));
            y_now=squeeze(dot_pos(j,:,2));
        end
        Dx=x_now-x_prev;
        Dy=y_now-y_prev;
        if dfns.ndots == 1
            if Dx <-1
                Dx=0;
                Dy=0;
            end
        else
            Dx(Dx<-1)=0;
            Dy(Dx<-1)=0;
        end
        for k=1:length(x_now)
            y_range=y_prev(k):(y_prev(k)+dot_size_px(2));
            x_range=x_prev(k):(x_prev(k)+dot_size_px(1));
            
            optic_flow(y_range,x_range,1,j-1)=Dx(k);
            optic_flow(y_range,x_range,2,j-1)=Dy(k);
        end
        x_prev=x_now;
        y_prev=y_now;
    end
    save(['true_optic_flow/' trialname '.mat'],'optic_flow')
end

