import re
import interpreter

class Script:
    def __init__(self, file=None):
        self.file = file
        self.variables = {}
        self.redefines = {}
        self.classes = {}

    def run(self, code=None):
        body = ""
        lines = None

        if code is not None:
            lines = code.split("\n")
        elif self.file is not None:
            print("Running script from path: {}".format(self.file.name))
            lines = self.file
        else:
            print("No code or file provided")
            return

        for line in lines:
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
            body = re.sub(re.escape(key) + '+(?=([^"]*"[^"]*")*[^"]*$)', value, body)

        # From body remove all spaces that aren't between quotes
        body = re.sub(r'\s+(?=([^"]*"[^"]*")*[^"]*$)', '', body)
        return interpreter.parse(self, body)

    def __handle_metatag(self, tag):
        if tag.startswith("wedefine"):
            tagArgs = tag.split(' ')

            if tagArgs[1].startswith('"'):
                index = tag.find('"', 1)
                index2 = tag.find('"', index + 1)
                key = tag[index + 1:index2]
                self.redefines[key] = tag[index2 + 2:]
            else:
                self.redefines[tagArgs[1]] = " ".join(tagArgs[2:])