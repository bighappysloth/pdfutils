import sys
import platform
import argparse
import pathlib
import io


from PyPDF2 import PdfReader, PdfWriter, PdfMerger, Transformation

parser = argparse.ArgumentParser()
parser.add_argument(
    "-input", "-i", type=pathlib.Path, required=True, help="File to Probe"
)
parser.add_argument(
    "-pages", "-p", type=int, nargs=2, required=True, help="page range to probe"
)

args = parser.parse_args()

if __name__ == "__main__":
    print("Platform Version:" + str(platform.python_version()))
    print("Input PDF: ", args.input, "\nPages: ", args.pages)

    # Debug Info
    with open(str(args.input), "rb") as f:  # Open Input PDF File
        reader = PdfReader(f)
        start_page = min(1, args.pages[0])
        pdf_pages = []
        for i in range(start_page, args.pages[1]):
            # dump said pages into here
            pdf_pages.append(reader.pages[i].extract_text())
        for z in pdf_pages:
            print(z, "\n\n", "=" * 4, "PAGE_SEPARATOR", "=" * 4, "\n\n\n")
