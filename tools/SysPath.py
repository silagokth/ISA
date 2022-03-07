import pathlib
import logging
import sys

class SysPath:
    def __init__(self):
        self.home_dir = pathlib.Path("~").resolve()
        self.curr_dir = pathlib.Path().resolve()
        self.prog_dir = pathlib.Path(__file__).parent.parent.resolve()
        self.temp_dir = pathlib.Path("/tmp").resolve()

    def find_config(self, name):
        if (self.curr_dir / name).is_file():
           return  (self.curr_dir / name).resolve()
        elif (self.home_dir / ".manas" /  name).is_file():
            return  (self.home_dir / ".manas" /  name).resolve()
        elif (self.prog_dir / "config" /  name).is_file():
            return (self.prog_dir / "config" /  name).resolve()
        else:
            logging.error("Cannot find config file: " + name)
            sys.exit()