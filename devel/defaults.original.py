import time.strftime
import textwrap.fill
import argparse.HelpFormatter

class TrialParameters(object):
    resource_path = 'resources'
    trial_path    = 'trial'
    png_path      = '{}/png'.format(trial_path)
    ndots         = 350
    res           = [1024,768]
    dot_size      = 20
    trial_name    = 'noisy_field-'+time.strftime('%Y:%m:%d:%H:%M:%S')

wrap=lambda s : textwrap.fill(s,80)
with open('MakeTrial.readme') as f:
    l=f.readlines()
    s=map(wrap,l)
    self.desc='\n'.join(s).strip('\n')

class CustomHelpFormatter(argparse.HelpFormatter):
    def _fill_text(self, text, width, indent):
        return ''.join([indent + line for line in text.splitlines(True)])
    def _get_help_string(self, action):
        help = action.help
        if '%(default)' not in action.help:
            if action.default is not argparse.SUPPRESS:
                defaulting_nargs = [argparse.OPTIONAL, argparse.ZERO_OR_MORE]
                if action.option_strings or action.nargs in defaulting_nargs:
                    help += ' (default: %(default)s)'
        return help

parser = argparse.ArgumentParser(description=defaults.desc,
                                 formatter_class=defaults.CustomHelpFormatter,
                                 fromfile_prefix_chars='@')



