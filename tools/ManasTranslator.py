#!/usr/bin/env python3

import sys
import re
import logging
import argparse
from InstructionSetArchitecture import InstructionSetArchitecture
from SysPath import SysPath

def build_node_map(line, isa, prefix, pc, node_map):
    result = re.match(r"\s*(\w+)\s+(.*)$", line)
    command = result.group(1)

    template = {}
    for tmp in isa["instruction_templates"]:
        if tmp["name"] ==  command:
            template = tmp
            break
    if template == {}:
        logging.error("Unrecongnized instruction:"+ command)
        sys.exit()
    
    for i in range(template["phase"]):
        node_map.add(prefix+"_"+str(pc)+"_"+str(i+1))

def translate_relation(line, isa, node_map):
    result = re.match(r'''\s*("[_\w]+")\s+(\d+)\s+(\d+)\s+\[([^\]]*)\]\s+\[([^\]]*)\]\s+(\d+)\s+$''', line)
    if not result:
        logging.error("Wrong relation: "+ line)
        sys.exit()
    
    list0 = []
    list1 = []
    if result.group(4):
        list0 = result.group(4).split(",")
        list0 = [re.search(r'''"(.*)"''', x).group(1) for x in list0]
        list00 = set()
        for pattern in list0:
            flag_matched = False
            for x in node_map:
                if re.match(pattern, x):
                    list00.add("\""+x+"\"")
                    flag_matched = True
            if not flag_matched:
                list00.add("\""+pattern+"\"")
        list0=list00

    if result.group(5):
        list1 = result.group(5).split(",")
        list1 = [re.search(r'''"(.*)"''', x).group(1) for x in list0]
        list11 = set()
        for pattern in list0:
            flag_matched = False
            for x in node_map:
                if re.match(pattern, x):
                    list11.add("\""+x+"\"")
                    flag_matched = True
            if not flag_matched:
                list11.add("\""+pattern+"\"")
        list1=list11
    
    output = result.group(1) + " " + result.group(2) + " "+ result.group(3) + " [" + ",".join(list0) + "] [" + ",".join(list1) + "] " + result.group(6) + "\n"
    return output

def translate(line, isa):
    result = re.match(r"\s*(\w+)\s+(.*)$", line)
    command = result.group(1)
    fields = result.group(2).split(",")

    output = command + " "

    template = {}
    for tmp in isa["instruction_templates"]:
        if tmp["name"] ==  command:
            template = tmp
            break
    if template == {}:
        logging.error("Unrecongnized instruction:"+ command)
        sys.exit()

    arguments = []
    for segment in template["segment_templates"]:
        if segment["controllable"]:
            arguments.append(segment)
    
    for x in arguments:
        x["value"] = str(x["default_val"])

    if len(fields) == 0 or (len(fields)==1 and fields[0]==''):
        pass
    else:
        for field in fields:
            rt = re.match(r"\s*([\w_]+)\s*=\s*([\w\d_]+)\s*", field)
            if not rt:
                logging.error("Unrecongnized field:"+ field)
                sys.exit()
            name = rt.group(1)
            value = rt.group(2)
            flag = False
            for x in arguments:
                if x["name"] == name:
                    x["value"] = value
                    for y in x["verbo_map"]:
                        if y["val"] == value:
                            x["value"] = str(y["key"])
                            break
                    if not x["value"].isnumeric():
                        logging.error("Bad field value for "+ command + " instruction: " + name + "=" + value + ". " + "Allowed fields are numbers or the follwoing macros: " + ", ".join(v["val"] for v in x["verbo_map"]))
                        sys.exit()
                    flag = True
                    break
            if not flag:
                logging.error("Unknown field name for "+ command + " instruction: " + name)
                sys.exit()
        
    for x in arguments:
        output = output + " " + x["value"]
    output = output + "\n"
    return output
    
def main():
    logging.basicConfig(format='%(asctime)s - %(levelname)s:\n%(message)s', level=logging.DEBUG)

    parser = argparse.ArgumentParser(description="Translate manas file according to ISA")
    parser.add_argument("input_file", help="Input file")
    parser.add_argument("output_file", help="Output file")
    args = parser.parse_args()

    sp = SysPath()
    isa_file = sp.find_config("isa.json")
    schema_file = sp.find_config("isa_schema.json")
    isa = InstructionSetArchitecture(isa_file, schema_file).get()

    # First round, build node map
    input_file = open(args.input_file, 'r')
    lines = input_file.readlines()
    translate_enable = False
    prefix = "Op_0_0"
    node_map = set()
    pc = {}
    pc[prefix] = 0
    for line in lines:
        if re.match("^\s*$", line):
            continue
        if translate_enable == False:
            if(re.search(r"\.CODE", line)):
                translate_enable = True
        else:
            if(re.search(r"\.DATA", line) or re.search(r"\.RELATION", line) or re.search(r"\.DEPENDENCY", line) ):
                translate_enable = False
            elif re.search(r"CELL", line):
                rt = re.search(r"CELL\s*<\s*(\d+)\s*,\s*(\d+)\s*>", line)
                if not rt:
                    logging.error("Syntax error near: " , line)
                    sys.exit()
                prefix = "Op_"+rt.group(1)+"_"+rt.group(2)
                if not (prefix in pc):
                    pc[prefix] = 0
            else:
                build_node_map(line, isa, prefix, pc[prefix], node_map)
                pc[prefix] = pc[prefix]+1

    # Second round, get all instructions
    with open(args.output_file, "w+") as f:
        input_file = open(args.input_file, 'r')
        lines = input_file.readlines()
        curr_section = ".DATA"
        for line in lines:
            if re.match("^\s*$", line):
                continue
            if(re.search(r"\.DATA", line)):
                curr_section = ".DATA"
                f.write(line)
            elif(re.search(r"\.CODE", line)):
                curr_section = ".CODE"
                f.write(line)
            elif(re.search(r"\.RELATION", line)):
                curr_section = ".RELATION"
                f.write(line)
            elif(re.search(r"\.DEPENDENCY", line)):
                curr_section = ".DEPENDENCY"
                f.write(line)
            else:
                if curr_section == ".CODE":
                    if re.search(r"CELL", line):
                        f.write(line)
                    else:
                        f.write(translate(line, isa))
                elif curr_section == ".RELATION":
                    f.write(translate_relation(line, isa, node_map))
                else:
                    f.write(line)
        
        f.write("\n")

if __name__ == "__main__":
    main()

