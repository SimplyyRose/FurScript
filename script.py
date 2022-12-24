import re
import interpreter

class Script:
    def __init__(self, file):
        self.file = file
        self.variables = {}

    def run(self):
        print("Running script from path: {}".format(self.file.name))

        body = ""

        for line in self.file:
            # Strip and ignore empty lines
            line = line.rstrip("\n")
            if line == "" or line.lstrip().startswith("//"): 
                continue
            # Continue to form body
            body += line

        # From body remove all spaces that aren't between quotes
        body = re.sub(r'\s+(?=([^"]*"[^"]*")*[^"]*$)', '', body)
        interpreter.parse(self, body)