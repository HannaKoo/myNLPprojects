#!/usr/bin/env python3

# 1. lists where the numbers are stored
# 2. the collection of documents

import re # regex library
import argparse # this library allows us to give arguments in the form of `python3 <script> --flags arguments`

# You need two files and run the script in the following way
# python3 HM.py --mapfile <mapping_file> --infile <collection_of_docs> --outfile <outfile>
# where

# the mapping file format
# one text + list every line
# e.g.
# exempli gratia: n. 5-7, 10, 25
# carpe diem: n. 8, 18, 28
# ...
# in the program, it will be turned into dictionary mapping words to the list
# mapping = {
#    "exempli gratia": [5, 6, 7, 10, 25],
#    "carpe diem": [8, 18, 28],
#    ...
# }

# the infile contains the collection of all the documents

# the outfile is the name of the output file that will be created as a result of this program

############### THE CODE STARTS HERE ###############

# 5-7, 10-25 -> 5,6,7 10,11,12,...
# function
# numbers = expand_number("1,2,3,6-10")
def expand_number(whole_string):
    """
    input (str): "1,2,3,6-10"
    output (list): [1,2,3,6,7,8,9,10]
    """
    whole_string = whole_string.replace(" ","").split(",")
    new_numbers = []
    for number in whole_string:
        if "-" in number:
            start, end = number.split("-")
            for n in range(int(start),int(end)):
                new_numbers.append(n)
        else:
            new_numbers.append(int(number))
    return new_numbers

# exempli gratia: n. 5-7, 10, 25
def read_mapping_file(filename):
    with open(filename, "r") as f:
        data = f.readlines()
    mapping = {}
    for line in data:
        line = line.strip()
        if not line: # skip empty lines just in case there are those
            continue
        m = re.match(r'(.*):\s+n\.\s+(\d.*)', line)
        mapping[m.group(1)] = expand_number(m.group(2))
    return mapping
        
# a function that parses the document
# when a new doc starts, it starts with
# <headingline><document>no.</document>...

def get_number(current_heading):
    """the function gets the number given the heading line"""
    m = re.match(r'\<headingline\>(\d+).*\<\/headingline\>', current_heading)
    assert m, "heading line format unexpected: {}".format(current_heading)
    return int(m.group(1))

def parse_doc(list_of_documents):
    """
    the function takes in the whole collection of documents in a list of lines
    returns a dictionary where the key is the integer and the value is a list [heading_line, other texts]
    {number: [heading_line, other texts]}
    """
    doc_dict = {}
    current_doc = []
    current_heading = ""
    header = []
    
    for line in list_of_documents:
        if line.strip().startswith("<headingline>"):
            if current_doc and current_heading: # adds a doc to the dictionary
                doc_dict[get_number(current_heading)] = [current_heading, "\n".join(current_doc)]
                current_doc = []
            elif current_doc:
                assert not header, "header already exists"
                header = current_doc.copy()
                current_doc = []
            current_heading = line.strip()
        elif line.strip(): # not empty line
            current_doc.append(line.strip())
        # empty lines are skipped
    if current_doc: # the last one also need to be added
        doc_dict[get_number(current_heading)] = [current_heading, "\n".join(current_doc)]
    return doc_dict, header
            
def insert_text(heading_line, text):
    """
    this function takes a heading line and a text to be added, and return a new heading line
    e.g. insert_text("<headingline>100<whatever_tags></headingline>", "exempli gratia")
         returns "<headingline>100<exempli gratia><whatever_tags></headingline>"
    """
    m = re.match(r'(<headingline>\d+)(.*<\/headingline>)', heading_line)
    new_heading = m.group(1)+"<"+text+">"+m.group(2)
    return new_heading

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--mapfile', required=True, help="path to a txt file with the mapping")
    parser.add_argument('--infile', required=True, help="path to the infile, which is the collection of documents to have tags added")
    parser.add_argument('--outfile', required=True, help="path to the outfile, which the modified tagged documents will be written to")
    args = parser.parse_args()

    # read the mapping file, returns
    # mapping = {
    #    "exempli gratia": [5, 6, 7, 10, 25],
    #    "carpe diem": [8, 18, 28],
    #    ...
    # }
    mapping = read_mapping_file(args.mapfile)
    
    # read in the whole document
    with open(args.infile, "rt") as f:
        document = f.readlines()

    doc_dict, header = parse_doc(document) # {number: [heading_line, other texts]}

    for text, doc_numbers in mapping.items():
        for doc_no in doc_numbers:
            heading_line, other_texts = doc_dict[doc_no]
            doc_dict[doc_no] = [insert_text(heading_line, text), other_texts]

    # write to file
    all_numbers = sorted(doc_dict.keys())
    with open(args.outfile, "wt") as f:
        f.write("\n".join(header))
        f.write("\n")
        for k in all_numbers:
            heading_line, other_texts = doc_dict[k]
            f.write(heading_line+"\n")
            f.write(other_texts+"\n")
            f.write("\n")
