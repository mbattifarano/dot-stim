import MakeTrial
import argparse

parser=argparse.ArgumentParser(prefix_chars=':')

parser.add_argument(':x','::cross',nargs='*',type=str)
parser.add_argument(':+','::add',nargs='*',type=str)

args=parser.parse_args()

print args
