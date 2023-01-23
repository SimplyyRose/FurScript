import re
import interpreter

class Script:
    def __init__(self, file):
        self.file = file
        self.variables = {}
        self.redefines = {}

    def run(self):
        print("Running script from path: {}".format(self.file.name))

        body = ""

        for line in self.file:
            # Strip and ignore empty lines
            line = line.rstrip("\n")
            if line == "" or line.lstrip().startswith("//"): 
                continue
            elif line.startswith("#"):
                # Handle metatags
                self.__handle_metatag(line[1:])
                continue
            # Continue to form body
            body += line

        for key, value in self.redefines.items():
            # From body regex replace all 'key' with 'value' that aren't between quotes
            body = re.sub(re.escape(key) + '+(?=([^"]*"[^"]*")*[^"]*$)', value, body)

        # From body remove all spaces that aren't between quotes
        body = re.sub(r'\s+(?=([^"]*"[^"]*")*[^"]*$)', '', body)
        interpreter.parse(self, body)

    def __handle_metatag(self, tag):
        if tag.startswith("wedefine"):
            tagArgs = tag.split(" ")
            self.redefines[tagArgs[1]] = " ".join(tagArgs[2:])
