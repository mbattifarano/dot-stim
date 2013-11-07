import stimulus

args='--segment-duration 60 --window-speed 0 --ndots 400 --dot-size 1  --field-size 5 --speed 8 --angle-var 4'.split()

trial=stimulus.Trial(*args)
trial.generate
