import os
import datetime
from script import Script

start = datetime.datetime.now()

# Create scripts folder if it doesn't exist
if not os.path.exists("scripts"):
    os.makedirs("scripts")

# Read files from scripts
for filename in os.listdir("scripts"):
    # Ignore non .py files
    if not filename.endswith(".fur"):
        continue

    # Open file
    file = open(os.path.join("scripts", filename))

    # Create script object
    s = Script(file)
    s.run()

end = datetime.datetime.now()
print("Run time: " + str(end - start))