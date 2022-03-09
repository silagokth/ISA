#!/usr/bin/env python3

import argparse
from InstructionSetArchitecture import InstructionSetArchitecture
import logging
from jinja2 import Template
from SysPath import SysPath

def main():
    logging.basicConfig(format='%(asctime)s - %(levelname)s:\n%(message)s', level=logging.DEBUG)

    parser = argparse.ArgumentParser(description="Generate markdown documentation according to ISA")
    parser.add_argument("output_file", help="Output markdown file")
    args = parser.parse_args()

    sp = SysPath()
    isa_file = sp.find_config("isa.json")
    schema_file = sp.find_config("isa_schema.json")
    isa = InstructionSetArchitecture(isa_file, schema_file).get()

    template = '''
{%- for i in instruction_templates %}

### {{i.name}}

Field | Position | Width | Default Value | Description
------|----------|-------|---------------|-------------------------
instr_code | [{{i.max_chunk*instr_bitwidth - 1}}, {{i.max_chunk*instr_bitwidth - instr_code_bitwidth}}] | {{instr_code_bitwidth}} | {{i.code}} | Instruction code for {{i.name}}
{%- set ns=namespace(index=i.max_chunk*instr_bitwidth - instr_code_bitwidth) -%}
{%- for j in i.segment_templates %}
{{j.name}} | [{{ns.index - 1 }}, {{ns.index - j.bitwidth}}] | {{j.bitwidth}} | {{j.default_val}} | {{j.comment}} {%- if j.verbo_map -%}{% for k in j.verbo_map %} [{{k.key}}]:{{k.val}};{% endfor %}{%- endif -%}
{%- set ns.index = ns.index - j.bitwidth -%}
{%- endfor -%}
{%- endfor -%}
'''
    t = Template(template)
    with open(args.output_file, "w+") as f:
        f.write(t.render(isa))

if __name__ == "__main__":
    main()

