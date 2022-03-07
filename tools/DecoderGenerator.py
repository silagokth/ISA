#!/usr/bin/env python3

import argparse
from InstructionSetArchitecture import InstructionSetArchitecture
import logging
from jinja2 import Template
from SysPath import SysPath

def main():
    logging.basicConfig(format='%(asctime)s - %(levelname)s:\n%(message)s', level=logging.DEBUG)

    parser = argparse.ArgumentParser(description="Generate unpacking functions for VHDL according to ISA")
    parser.add_argument("output_file", help="Output VHDL file")
    args = parser.parse_args()
    
    sp = SysPath()
    isa_file = sp.find_config("isa.json")
    schema_file = sp.find_config("isa_schema.json")
    isa = InstructionSetArchitecture(isa_file, schema_file).get()

    template = '''
-- !!! AUTOMATICALLY GENERATED FILE, DON'T EDIT IT !!!

--~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
--                                                                         #
--This file is part of SiLago.                                             #
--                                                                         #
--    SiLago platform source code is distributed freely: you can           #
--    redistribute it and/or modify it under the terms of the GNU          #
--    General Public License as published by the Free Software Foundation, #
--    either version 3 of the License, or (at your option) any             #
--    later version.                                                       #
--                                                                         #
--    SiLago is distributed in the hope that it will be useful,            #
--    but WITHOUT ANY WARRANTY; without even the implied warranty of       #
--    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the        #
--    GNU General Public License for more details.                         #
--                                                                         #
--    You should have received a copy of the GNU General Public License    #
--    along with SiLago.  If not, see <https://www.gnu.org/licenses/>.     #
--                                                                         #
--~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

LIBRARY ieee, work;
USE ieee.std_logic_1164.ALL;
USE ieee.numeric_std.ALL;

PACKAGE isa_package IS
    {% for i in instruction_templates %}
    TYPE {{i.name}}_instr_type IS RECORD
        {%- if instr_code_bitwidth==1 %}
        instr_code : STD_LOGIC;
        {%- else %}
        instr_code : STD_LOGIC_VECTOR({{instr_code_bitwidth}} - 1 DOWNTO 0);
        {%- endif %}
        {%- for j in i.segment_templates %}
        {%- if j.observable %}
        {%- if j.bitwidth==1 %}
        {{j.name}} : STD_LOGIC;
        {%- else %}
        {{j.name}} : STD_LOGIC_VECTOR({{j.bitwidth}} - 1 DOWNTO 0);
        {%- endif %}
        {%- endif %}
        {%- endfor %}
    END RECORD;
    {%- endfor %}

    {% for i in instruction_templates -%}
    {%- if i.max_chunk > 1 -%}
    {%- for j in range(i.max_chunk) %}
    FUNCTION unpack_{{i.name}}{{j+1}}_record(arg : std_logic_vector({{instr_bitwidth * (j+1)}} - 1 DOWNTO 0)) RETURN {{i.name}}_instr_type;
    {%- endfor -%}
    {%- else %}
    FUNCTION unpack_{{i.name}}_record(arg : std_logic_vector({{instr_bitwidth}} - 1 DOWNTO 0)) RETURN {{i.name}}_instr_type;
    {%- endif -%}
    {%- endfor %}
END;

PACKAGE BODY isa_package IS
    {% for i in instruction_templates %}
    {%- if i.max_chunk > 1 %}
    {%- for j in range(i.max_chunk) %}
    FUNCTION unpack_{{i.name}}{{j+1}}_record(arg : std_logic_vector({{instr_bitwidth * (j+1)}} - 1 DOWNTO 0)) RETURN {{i.name}}_instr_type IS
        VARIABLE result : {{i.name}}_instr_type;
    BEGIN
        {%- if instr_bitwidth==1 %}
        result.instr_code := arg({{instr_bitwidth * (j+1) - 1}});
        {%- else %}
        result.instr_code := arg({{instr_bitwidth * (j+1) - 1}} DOWNTO {{instr_bitwidth * (j+1) - instr_code_bitwidth}});
        {%- endif %}
        {%- set ns = namespace(index=instr_bitwidth * (j+1) - instr_code_bitwidth) -%}
        {%- for k in i.segment_templates %}
        {%- if k.observable %}
        {%- if ns.index - k.bitwidth >= 0 %}
        {%- if k.bitwidth==1 %}
        result.{{k.name}} := arg({{ns.index - 1}});
        {%- else %}
        result.{{k.name}} := arg({{ns.index - 1}} DOWNTO {{ns.index - k.bitwidth}});
        {%- endif %}
        {%- else %}
        {%- if k.bitwidth==1 %}
        result.{{k.name}} := '{{k.default_val}}';
        {%- else %}
        result.{{k.name}} := std_logic_vector(to_unsigned({{k.default_val}}, {{k.bitwidth}}));
        {%- endif %}
        {%- endif %}
        {%- endif %}
        {%- set ns.index = ns.index - k.bitwidth -%}
        {%- endfor %}
        RETURN result;
    END;
    {%- endfor -%}
    {%- else %}
    FUNCTION unpack_{{i.name}}_record(arg : std_logic_vector({{instr_bitwidth}} - 1 DOWNTO 0)) RETURN {{i.name}}_instr_type IS
        VARIABLE result : {{i.name}}_instr_type;
    BEGIN
        {%- if instr_bitwidth==1 %}
        result.instr_code := arg({{instr_bitwidth - 1}});
        {%- else %}
        result.instr_code := arg({{instr_bitwidth - 1}} DOWNTO {{instr_bitwidth - instr_code_bitwidth}});
        {%- endif %}
        {%- set ns = namespace(index=instr_bitwidth - instr_code_bitwidth) -%}
        {%- for k in i.segment_templates %}
        {%- if k.observable %}
        {%- if k.bitwidth==1 %}
        result.{{k.name}} := arg({{ns.index - 1}});
        {%- else %}
        result.{{k.name}} := arg({{ns.index - 1}} DOWNTO {{ns.index - k.bitwidth}});
        {%- endif %}
        {%- endif %}
        {%- set ns.index = ns.index - k.bitwidth -%}
        {%- endfor %}
        RETURN result;
    END;
    {%- endif %}
    {% endfor %}
END;
'''
    t = Template(template)
    with open(args.output_file, "w+") as f:
        f.write(t.render(isa))

if __name__ == "__main__":
    main()

