import sys
import platform
import argparse
import pathlib



from PyPDF2 import PdfReader, PdfWriter
from decimal import Decimal

parser = argparse.ArgumentParser()
# We define the arguments here
# Syntax for defining arguments
# parser.add_argument('--values', type=int, nargs = 3)

#parser.add_argument('-o', type=str, nargs = 1, required=True, help='Output file name')

subparser = parser.add_subparsers(dest='command')
subparser.required = True

merge_parser = subparser.add_parser('merge')
toc_parser = subparser.add_parser('toc')
margin_parser = subparser.add_parser('margin')

merge_parser.add_argument('-input', type=pathlib.Path, nargs='+', required=True, help='Input file path, required')
merge_parser.add_argument('-output', type=str, nargs=1, required=False, help='Output file path (optional), default = first_input_file_M.pdf') #optional output argument

toc_parser.add_argument('-input', type=pathlib.Path, nargs=1, required=True, help='Input PDF path, required')
toc_parser.add_argument('-config', type=pathlib.Path, nargs=1, required=True, help='Input config path, required')
toc_parser.add_argument('-output', type=pathlib.Path, nargs=1, required=False, help='Output file path (optional)')

margin_parser.add_argument('-input', type=pathlib.Path, nargs='+', required=True, help='Input file path, required')
margin_parser.add_argument('-margin_size', type=float, nargs=1, required=False, help='Absolute Horizontal Margin Size (optional), default = 180')
margin_parser.add_argument('-z', type=float, nargs=1, required=False, help='z Factor (optional), default = 0.65')
margin_parser.add_argument('-scale', type=float, nargs=1, required=False, help='Scaling Factor, resizes the pdf (optional), default = 0.25')

# TOC Parser Syntax
# L1 lk

#finish the args thing
args = parser.parse_args()


def tocManager(z):

	# Output File Name can be Modified
	if args.o: 
		oname = str(o) 
	else: 
		oname = z[:-4]+str('_TOC')+z[-4:]
	print('tocManager outputting to :' + oname)

	with open(z,'rb') as f:
		writer = PdfWriter()
		reader = PdfReader(f)
		
		print('Number of Pages: ' + str(reader.numPages)+ '\n' + 'Outline: ' + str(reader.outline))

		r_outline = reader.outline
		print('Outline Length: ' + str(len(reader.outline)))
		print('Outline Entry Keys: ' + str(reader.outline[0].keys()))

		#add all the magic pages
		writer.clone_document_from_reader(reader)
		#Now we can manipulate the table of contents.
		
		#writer.add_outline()

		#print('get_named_dest_root():' + str(writer.get_named_dest_root()))
		
		print('get_outline_root():' + writer.get_outline_root())
		x = {'title': 'Page 2','pagenum': 2,'parent': writer.get_outline_root()}
		
		writer.add_outline_item(*x)
		#with open(oname, "wb") as fp:
		# 	writer.write(fp)



if __name__ == '__main__':

	print('Platform Verison:' + str(platform.python_version()))
	print('Command Chosen: ' + args.command)
	if args.command=='toc':
		
		# Read the config file. Separate by lines
		with args.config[0].open() as f:
			lines = f.read().splitlines()
			for i in range(0,len(lines)):
				
				temp = lines[i]
				#print('temp' + str(i) + ' ' + str(temp))
				lines[i] = temp.split('$')
				temp_indent_level = len(lines[i][0])-len(lines[i][0].lstrip())
				lines[i][0]=lines[i][0].lstrip()
				lines[i].append(temp_indent_level)
				lines[i]={'pagenum': int(lines[i][0]), 'title': str(lines[i][1]),'indent_level': int(lines[i][-1])}
				
				# {'pagenum': 1, 'title': 'Chapter 1', 'indent_level': 0}
				# {'pagenum': 4, 'title': 'Chapter 1.1', 'indent_level': 1}
				# {'pagenum': 5, 'title': 'Chapter 1.2.1', 'indent_level': 2}
				# {'pagenum': 7, 'title': 'Chapter 1.3', 'indent_level': 1}
				# {'pagenum': 12, 'title': 'Chapter 2', 'indent_level': 0}
				print(lines[i])
			
			#Now we have a valid 'lines' list of dictionaries.
			#Traverse it like a stack structure.
			config_outline_structure = []
			temp_stack = []

			for i in range(0,len(lines)):
				current_indent_level = lines[i]['indent_level']
				if i==0: 
					previous_indent_level = 0
				else:
					previous_indent_level = lines[i-1]['indent_level']
				
				if current_indent_level==previous_indent_level:
					# If the temp_stack is not empty then we pop the last one,
					# config_outline_structure keeps track of indent_level 0 entries.
					if len(temp_stack) !=0:
						config_outline_structure(temp_stack.pop())

					lines[i]=lines.del('indent_level') # no need to keep track of this
					config_outline_structure.append(lines[i])
				elif current_indent_level>= 1 and current_indent_level > previous_indent_level:
					# Handling the case where it goes into a subchapter.
					# There has to be an existing previous line or else it won't work. We must check that the first line cannot be indented in the beginning too.
					




				#implement logic here
				print(current_indent_level)

	#tocManager(fname)
	print('Terminating Program...')