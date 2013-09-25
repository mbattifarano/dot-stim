import subprocess as sh
import sys

def main(trialname):
    for trial in trialname:
        path_to_trial = 'trials/{}'.format(trial)
        sh.check_call(['rm','-r',path_to_trial])

if __name__=='__main__':
    main(sys.argv[1:])
