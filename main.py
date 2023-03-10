import os
import datetime
import sys
from script import Script

start = datetime.datetime.now()

# Create scripts folder if it doesn't exist
if not os.path.exists("scripts"):
    os.makedirs("scripts")

if sys.argv.__len__() > 1:
    file = open(sys.argv[1], encoding='utf-8')
    s = Script(file)
    s.run()
else:
    # Read files from scripts
    for filename in os.listdir("scripts"):
        # Ignore non .py files
        if not filename.endswith(".fur"):
            continue

        # Open file
        file = open(os.path.join("scripts", filename), encoding='utf-8')

        # Create script object
        s = Script(file)
        s.run()

end = datetime.datetime.now()
print(f"Time taken: {end - start} seconds")