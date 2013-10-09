import MakeTrial
import argparse
import textwrap

wrap=lambda s : textwrap.fill(s,80)
with open('MakeTrial2.readme') as f:
    l=f.readlines()
    s=map(wrap,l)
    desc='\n'.join(s).strip('\n')

# Combine RawText and ArgumentDefaults help formatters and line wrap pre-print
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

parser=argparse.ArgumentParser( description=desc,
                                prefix_chars=':',
                                formatter_class=CustomHelpFormatter)

parser.add_argument(':x','::cross',nargs='*',type=str)
parser.add_argument(':+','::add',nargs='*',type=str)
parser.add_argument(':*','::inner',nargs='*',type=str)
parser.add_argument(':r','::rand',action='store_true')
parser.add_argument(':l','::loop',type=int,default=1)

args=parser.parse_args()

print args
