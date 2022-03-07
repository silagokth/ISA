#!/usr/bin/env python3

import sys
import json
import jsonschema
import logging

class InstructionSetArchitecture:
    def __init__(self, json_file, schema_file):
        try:
            with open(json_file, "r") as json_f:
                self.isa = json.load(json_f)
        except IOError:
            logging.error("Can't open file: " + json_file)
            sys.exit()

        try:
            with open(schema_file, "r") as schema_f:
                self.schema = json.load(schema_f)
        except IOError:
            logging.error("Can't open file: " + schema_f)
            sys.exit()

        self.validate()
        self.load()

    def validate(self):
        """Validate the isa json file against a schema."""
        jsonschema.validate(instance=self.isa, schema=self.schema)

    def load(self):
        """Load isa from a json file and complete the optional fields."""
        for t in self.isa["instruction_templates"]:
            if not "phase" in t:
                t["phase"] = 1
            if not "max_chunk" in t:
                t["max_chunk"] = 1
            for tt in t["segment_templates"]:
                if not "verbo_map" in tt:
                    tt["verbo_map"] = {}
                if not "default_val" in tt:
                    tt["default_val"] = 0
                if not "controllable" in tt:
                    tt["controllable"] = True
                if not "observable" in tt:
                    tt["observable"] = True
    
    def save(self, filename):
        """Save the ISA to file."""
        try:
            with open(filename, "w+") as f:
                f.write(self.isa)
        except IOError:
            logging.error("Can't open file: " + filename)
            sys.exit()

    def get(self):
        """Return the isa object"""
        return self.isa
