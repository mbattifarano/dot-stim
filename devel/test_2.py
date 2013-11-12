import stimulus
import matlab

stim_spec=[]
#stim_spec.append('--fix-dur 10 --segment-duration 80 --field-center -2 0 --window-speed 10 --dot-density 4 --dot-size 0.09 --field-size 2.5 --speed 10 --trial-name patch0ns10dpslong2 --end-jump')

stim_spec.append('--fix-dur 10 --segment-duration 160 --field-center -4 0 --window-speed 10 --dot-density 4 --dot-size 0.09 --field-size 2.5 --speed 4 --angle-var 40 --trial-name patch4ns10dpslong2  --end-jump')

#stim_spec.append('--fix-dur 10 --segment-duration 80 --field-center -2 0 --window-speed 4 --dot-density 4 --dot-size 0.09 --field-size 2.5 --speed 4 --angle-var 40 --trial-name patch4ns4dpslong --end-jump')

#stim_spec.append('--fix-dur 10 --segment-duration 2000 --field-center 0 0 --window-speed 0 --ndots 200 --dot-size 0.06 --field-size 5 --speed 1 --angle-var 40 --trial-name swsh4ns200dotslargelong2')

#stim_spec.append('--fix-dur 10 --segment-duration 80 --field-center 0 0 --window-speed 0 --ndots 400 --dot-size 0.03 --field-size 5 --speed 8 --angle-var 40 --trial-name swsh4ns400dots')

#stim_spec.append('--fix-dur 10 --segment-duration 80 --field-center -2 0 --window-speed 8 --ndots 400 --dot-size 0.03 --field-size 5 --speed 8 --angle-var 40 --trial-name swsh4ns400dotstrans --end-jump')

#stim_spec.append('--fix-dur 10 --segment-duration 80 --field-center 0 0 --window-speed 0 --ndots 400 --dot-size 0.09 --field-size 5 --speed 8 --angle-var 40 --trial-name swsh4ns400dotslargelong')

#stim_spec.append('--fix-dur 10 --segment-duration 80 --field-center -8 0 --window-speed 8 --ndots 400 --dot-size 0.09 --field-size 5 --speed 8 --angle-var 40 --trial-name swsh4ns400dotstranslargelong --end-jump')

#stim_spec.append('--fix-dur 10 --segment-duration 80 --window-speed 15 --ndots 1 --dot-size 0.25 --field-size 0.25 --speed 0 --trial-name spot15dps --end-jump')
#stim_spec.append('--fix-dur 10 --segment-duration 80 --window-speed 13.5 --ndots 1 --dot-size 0.25 --field-size 0.25 --speed 0 --trial-name spot13.5dps --end-jump')
#stim_spec.append('--fix-dur 10 --segment-duration 80 --window-speed 12 --ndots 1 --dot-size 0.25 --field-size 0.25 --speed 0 --trial-name spot12dps --end-jump')
#stim_spec.append('--fix-dur 10 --segment-duration 80 --window-speed 16.5 --ndots 1 --dot-size 0.25 --field-size 0.25 --speed 0 --trial-name spot16.5dps --end-jump')
#stim_spec.append('--fix-dur 10 --segment-duration 80 --window-speed 18 --ndots 1 --dot-size 0.25 --field-size 0.25 --speed 0 --trial-name spot18dps --end-jump')

for args in stim_spec:
    arg_list=args.split()
    print arg_list
    trial=stimulus.Trial(*arg_list)
    trial.generate()

#matlab.matlab('import_stim_png','{swsh4ns400dotslarge}')
