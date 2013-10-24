cl
load('filter_test.mat')

Fs = double(sample_rate);     % Sampling frequency
T = 1/Fs;                     % Sample time
L = length(sample_in);        % Length of signal
t = (0:L-1)*T;                % Time vector

figure;
subplot(2,1,1)
    plot(Fs*t,sample_in)
    title('sample in')
    xlabel('time')
subplot(2,1,2)
    plot(Fs*t,sample_out)
    title('sample out')
    xlabel('time')

NFFT = 2^nextpow2(L); % Next power of 2 from length of y
X = fft(sample_in,NFFT)/L;
Y = fft(sample_out,NFFT)/L;
f = Fs/2*linspace(0,1,NFFT/2+1);

% Plot single-sided amplitude spectrum.
figure;
subplot(2,1,1)
    plot(f,2*abs(X(1:NFFT/2+1))) 
    title(['Single-Sided Amplitude Spectrum of filter input (' num2str(cut_off) ' Hz)'])
    xlabel('Frequency (Hz)')
    ylabel('|X(f)|')
subplot(2,1,2)
    plot(f,2*abs(Y(1:NFFT/2+1))) 
    title('Single-Sided Amplitude Spectrum of filter output')
    xlabel('Frequency (Hz)')
    ylabel('|Y(f)|')