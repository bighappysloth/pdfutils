import sys
import platform
import argparse
import pathlib
import io


from PyPDF2 import PdfReader, PdfWriter, PdfMerger, Transformation
from decimal import Decimal

parser = argparse.ArgumentParser()
# We define the arguments here
# Syntax for defining arguments
# parser.add_argument('--values', type=int, nargs = 3)

# parser.add_argument('-o', type=str, nargs = 1, required=True, help='Output file name')

subparser = parser.add_subparsers(dest="command")
subparser.required = True

# Subparsers, three functions
merge_parser = subparser.add_parser("merge")
toc_parser = subparser.add_parser("toc")
margin_parser = subparser.add_parser("margin")
extract_parser = subparser.add_parser("extract")

merge_parser.add_argument(
    "-input",
    type=pathlib.Path,
    nargs="+",
    required=True,
    help="Input file path, required",
)
merge_parser.add_argument(
    "-output",
    type=str,
    nargs=1,
    required=False,
    help="Output file path (optional), default = first_input_file_M.pdf",
)  # optional output argument
merge_parser.add_argument(
    "-inherit_toc", type=bool, nargs=1, required=False, help="Inherit TOC from subfile"
)
merge_parser.add_argument(
    "-add_blank_page_after_subfile",
    "-add_blank",
    action="store_true",
    help="Add Blank Page after each subfile? (uses size of last page)",
)


# TOC_Parser Arguments
toc_parser.add_argument(
    "-input", type=pathlib.Path, nargs=1, required=True, help="Input PDF path, required"
)
toc_parser.add_argument(
    "-config",
    type=pathlib.Path,
    nargs=1,
    required=True,
    help="Input config path, required",
)
toc_parser.add_argument(
    "-output",
    type=pathlib.Path,
    nargs=1,
    required=False,
    help="Output file path (optional)",
)
toc_parser.add_argument(
    "-offset", type=int, required=False, help="Offset by Positive number of pages"
)


# Margin Parser Arguments
margin_parser.add_argument(
    "-input",
    type=pathlib.Path,
    nargs="+",
    required=True,
    help="Input file path, required",
)
margin_parser.add_argument(
    "-margin_size",
    type=float,
    nargs=1,
    required=False,
    help="Absolute Horizontal Margin Size (optional), default = 180",
)
margin_parser.add_argument(
    "-z",
    type=float,
    nargs=1,
    required=False,
    help="z Factor (optional), default = 0.65",
)
margin_parser.add_argument(
    "-scale",
    type=float,
    nargs=1,
    required=False,
    help="Scaling Factor, resizes the pdf (optional), default = 0.25",
)

# image extract parser arguments
extract_parser.add_argument(
    "-input",
    "-i",
    type=pathlib.Path,
    nargs=1,
    required=True,
    help="Input file path, required",
)

# TOC Parser Syntax
# L1 lk

# finish the args thing
args = parser.parse_args()


def marginManager(path, margin, sf, z):
    with open(path, "rb") as f:
        p = PdfReader(f)

        writer = PdfWriter()
        path = str(path)
        print("filename: " + path)
        print("printing p pages: " + str(p.pages))
        print("0 page?:" + str(p.pages[0]))
        for i in range(len(p.pages)):
            page = p.pages[i]
            if page == None:
                print("EEEEE: ISNONE: " + str(i))

            w = float(page.mediabox.getWidth())
            h = float(page.mediabox.getHeight())

            print(
                "\tpagenum: "
                + str(i)
                + " size: "
                + str(w)
                + "/"
                + str(h)
                + "="
                + str(w / h)
            )
            new_page = writer.addBlankPage(w * sf + 2 * margin, h * sf + z * margin)
            translation = Transformation().translate(
                tx=float(margin), ty=float(z / 2.0) * margin
            )
            page.add_transformation(translation)
            new_page.merge_page(page, expand=False)

        fo_name = (
            path[:-4] + "_E" + path[-4:]
        )  # attach _E at the end of the time, before extension, the file name is fixed and cannot be changed.

        with open(fo_name, "wb") as fo:
            writer.write(fo)


# Require: List of Files, (array)
# Name of Output
# Add Blank Page between Files? (Bool)
# Import Subfile Outilnes? (Bool)
def mergeManager(list_of_files, output_name, add_blank_page_after_subfile, inherit_toc):
    m = PdfMerger(strict=False)

    print("Outputting to: " + str(output_name))
    for z in list_of_files:  # List of files
        with open(z, "rb") as f:
            print("Appending " + str(z))
            writer_to_flush = PdfWriter()
            writer_to_flush.append_pages_from_reader(PdfReader(f, strict=False))
            if add_blank_page_after_subfile:
                writer_to_flush.add_blank_page()  # Use the size of the last page
            tmp = io.BytesIO()
            writer_to_flush.write(tmp)
            m.append(
                tmp, outline_item=z[:-4], import_outline=inherit_toc
            )  # Add outline
    with open(str(output_name), "wb") as fo:
        m.write(fo)
        print("Writing to " + str(output_name))


def printTocOutline(z):
    tab_spacing = "\t" * z["indent_level"]
    print(tab_spacing + z["title"] + " --> " + str(z["pagenum"]) + "\n")
    if z.get("children"):
        for c in z["children"]:
            printTocOutline(c)


def recursiveToc(z, parent, parent_outline, writer):
    z_params = {"title": z["title"], "pagenum": z["pagenum"], "parent": parent_outline}
    z_outline = writer.add_outline_item(**z_params)  # Top level
    if z.get("children"):
        for c in z["children"]:
            recursiveToc(c, z, z_outline, writer)
    return z_outline


def tocManager(z, toc_structure):
    # Output File Name can be Modified
    # if args.o:
    # 	oname = str(o)
    # else:
    oname = z[:-4] + str("_TOC") + z[-4:]
    print("tocManager outputting to :" + oname)

    with open(z, "rb") as f:
        writer = PdfWriter()
        reader = PdfReader(f)

        print(
            "Number of Pages: "
            + str(reader.numPages)
            + "\n"
            + "Outline: "
            + str(reader.outline)
        )

        r_outline = reader.outline
        print("Outline Length: " + str(len(reader.outline)))
        if len(reader.outline) != 0:
            print("Outline Entry Keys: " + str(reader.outline[0].keys()))

        # add all the magic pages
        writer.clone_document_from_reader(reader)
        # Now we can manipulate the table of contents.

        # writer.add_outline()

        # print('get_named_dest_root():' + str(writer.get_named_dest_root()))

        print("get_outline_root():" + str(writer.get_outline_root()))
        outline_root = writer.get_outline_root()
        for y in toc_structure:
            y_params = {
                "title": y["title"],
                "pagenum": y["pagenum"],
                "parent": outline_root,
            }
            y_outline = writer.add_outline_item(**y_params)  # Top level
            if y.get("children"):
                for c in y["children"]:
                    recursiveToc(c, y, y_outline, writer)
        writer.page_mode = "/UseOutlines"
        with open(oname, "wb") as fp:
            writer.write(fp)


def extract_manager(z):
    with open(z, "rb") as f:
        reader = PdfReader(f)

        count = 0
        for i in range(0, len(reader.pages)):
            page = reader.pages[i]
            for image_file_object in page.images:
                im_name = z.parent.joinpath(
                    str(
                        str(z.stem)
                        + "_PAGE"
                        + str(i)
                        + "_"
                        + str(count)
                        + "_"
                        + image_file_object.name
                    )
                )
                with open(im_name, "wb") as fp:
                    fp.write(image_file_object.data)
                    count += 1


if __name__ == "__main__":
    print("Platform Verison:" + str(platform.python_version()))
    print("Command Chosen: " + args.command)
    if args.command == "toc":
        # Read the config file. Separate by lines
        with args.config[0].open() as f:
            lines = f.read().splitlines()
            offset = 0
            if args.offset:
                offset = int(args.offset)
            for i in range(0, len(lines)):
                temp = lines[i]
                # print('temp' + str(i) + ' ' + str(temp))
                lines[i] = temp.split("$")
                temp_indent_level = len(lines[i][0]) - len(lines[i][0].lstrip())
                lines[i][0] = lines[i][0].lstrip()
                lines[i].append(temp_indent_level)
                lines[i] = {
                    "pagenum": int(lines[i][0]) + offset,
                    "title": str(lines[i][1]),
                    "indent_level": int(lines[i][-1]),
                }

                # {'pagenum': 1, 'title': 'Chapter 1', 'indent_level': 0}
                # {'pagenum': 4, 'title': 'Chapter 1.1', 'indent_level': 1}
                # {'pagenum': 5, 'title': 'Chapter 1.2.1', 'indent_level': 2}
                # {'pagenum': 7, 'title': 'Chapter 1.3', 'indent_level': 1}
                # {'pagenum': 12, 'title': 'Chapter 2', 'indent_level': 0}
                # print(lines[i])

            # Now we have a valid 'lines' list of dictionaries.
            # Traverse it like a stack structure.
            config_outline_structure = []
            temp_stack = []

            for i in range(0, len(lines)):
                previous_indent_level = len(temp_stack) - 1  # keeps track of hierarchy
                current_indent_level = lines[i]["indent_level"]
                # print('current/prev indent_level' + str(current_indent_level)+'/'+str(previous_indent_level))

                if current_indent_level == previous_indent_level:
                    # If the temp_stack is not empty then we pop the last one,
                    # config_outline_structure keeps track of indent_level 0 entries.
                    if (
                        previous_indent_level == 0
                    ):  # if on the same indent level, and if indent level is root for example [Chapter 1], meets 'Chapter 2'
                        config_outline_structure.append(
                            temp_stack.pop()
                        )  # pop to root directory.

                    else:
                        # [Chapter 1, Chapter 1.1] meets 'Chapter 1.2'.
                        # pop Chapter 1.1, and append Chapter 1.2 to Chapter 1,
                        # then append Chapter 1.2 to the temp_stack in anticipation for Chapter 1.2.1

                        temp_stack.pop()  # pop the brother,

                        # This part fixes the last entry, as in 'Chapter 1'
                        last_entry = temp_stack.pop()

                        if last_entry.get("children"):
                            last_entry["children"].append(lines[i])
                        else:
                            last_entry["children"] = [lines[i]]
                        temp_stack.append(last_entry)

                    # always append to temp_stack the current line.
                    temp_stack.append(lines[i])
                    # print(temp_stack)

                elif current_indent_level > previous_indent_level:
                    # Handling the case where it goes into a subchapter.
                    # There has to be an existing previous line or else it won't work. We must check that the first line cannot be indented in the beginning too.

                    if previous_indent_level == -1:  # pushing the first element.
                        temp_stack.append(lines[i])
                        # print('Pushing First Element')
                        # print(temp_stack)
                    else:
                        # Modification of the last entry.
                        last_entry = temp_stack.pop()
                        if last_entry.get("children"):
                            last_entry["children"].append(lines[i])
                        else:
                            last_entry["children"] = [lines[i]]
                        temp_stack.append(last_entry)
                        temp_stack.append(lines[i])
                        # print(temp_stack)

                else:
                    # Now we have to pop enough entries within the temp_stack.
                    while current_indent_level < previous_indent_level:
                        temp_entry = temp_stack.pop()
                        if temp_entry["indent_level"] == 0:
                            config_outline_structure.append(
                                temp_entry
                            )  # only append to config_outline_structure if and only if it belongs to the root directory.
                        previous_indent_level = len(temp_stack) - 1
                    if current_indent_level == previous_indent_level:
                        # If the temp_stack is not empty then we pop the last one,
                        # config_outline_structure keeps track of indent_level 0 entries.
                        if (
                            previous_indent_level == 0
                        ):  # if on the same indent level, and if indent level is root for example [Chapter 1], meets 'Chapter 2'
                            config_outline_structure.append(
                                temp_stack.pop()
                            )  # pop to root directory.

                        else:
                            # [Chapter 1, Chapter 1.1] meets 'Chapter 1.2'.
                            # pop Chapter 1.1, and append Chapter 1.2 to Chapter 1,
                            # then append Chapter 1.2 to the temp_stack in anticipation for Chapter 1.2.1

                            temp_stack.pop()  # pop the brother,

                            # This part fixes the last entry, as in 'Chapter 1'
                            last_entry = temp_stack.pop()

                            if last_entry.get("children"):
                                last_entry["children"].append(lines[i])
                            else:
                                last_entry["children"] = [lines[i]]
                            temp_stack.append(last_entry)

                        # always append to temp_stack the current line.

                        # print(temp_stack)

                    elif current_indent_level > previous_indent_level:
                        # Handling the case where it goes into a subchapter.
                        # There has to be an existing previous line or else it won't work. We must check that the first line cannot be indented in the beginning too.

                        if previous_indent_level == -1:  # pushing the first element.
                            temp_stack.append(lines[i])
                            # print('Pushing First Element')
                            # print(temp_stack)
                        else:
                            # Modification of the last entry.
                            last_entry = temp_stack.pop()
                            if last_entry.get("children"):
                                last_entry["children"].append(lines[i])
                            else:
                                last_entry["children"] = [lines[i]]
                            temp_stack.append(last_entry)
                    temp_stack.append(lines[i])
                    # print(temp_stack)

                # print(temp_stack)
            while len(temp_stack) != 0:
                last_entry = temp_stack.pop()
                if last_entry["indent_level"] == 0:
                    config_outline_structure.append(last_entry)
                # implement logic here
            for x in config_outline_structure:
                printTocOutline(x)
            tocManager(str(args.input[0]), config_outline_structure)

    # def mergeManager(list_of_files, output_name, add_blank_pages_between_files,import_file_outlines):
    elif args.command == "merge":
        # generate default file name FIRSTFILE_M.pdf

        valid_files = []
        for z in args.input:  # admit valid files only
            if str(z)[-4:] == ".pdf" and str(z)[-6:] != "_M.pdf":
                valid_files.append(str(z))
        default_output_name = sorted(valid_files)[0]
        default_output_name = (
            default_output_name[:-4] + str("_M") + default_output_name[-4:]
        )

        merge_args = {
            "list_of_files": valid_files,
            "output_name": default_output_name,
            "add_blank_page_after_subfile": args.add_blank_page_after_subfile,
            "inherit_toc": args.inherit_toc,
        }

        if args.output:
            merge_args["output_name"] = args.output[0]
        mergeManager(**merge_args)
    elif args.command == "margin":
        # defaults
        default_margin = 180
        default_z = 0.65
        default_sf = 1.0
        if args.margin_size:
            default_margin = args.margin_size
        if args.z:
            default_z = args.z
        if args.scale:
            default_sf = args.scale
        for x in args.input:
            if str(x)[-4:] == ".pdf" and str(x)[-6:] != "_E.pdf":
                marginManager(x, default_margin, default_sf, default_z)
    elif args.command == "extract":
        extract_manager(args.input[0])
    print("Terminating Program...")
