#!/usr/bin/env python3

import os
from SysPath import SysPath

sp = SysPath()
DecoderGenerator = sp.prog_dir / "tools" / "DecoderGenerator.py"
DocGenerator = sp.prog_dir / "tools" / "DocGenerator.py"
vhdl_file = sp.prog_dir / "config" / "isa.vhdl"
markdown_file = sp.prog_dir / "config" / "isa.md"
os.system("python3 {} {}".format(DecoderGenerator.resolve(), vhdl_file.resolve()))
os.system("python3 {} {}".format(DocGenerator.resolve(), markdown_file.resolve()))