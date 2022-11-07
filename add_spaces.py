#add spaces
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-s',type=str,required=True)
args = parser.parse_args()

z = ''
for c in args.s:
    z = z + c + '\s?'
print(z)