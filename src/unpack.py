# Import module
from utils.graphics import Graphics
from utils.sprite import Sheet
from utils.file import File
import sys

File.setImageHeight(30)

if len(sys.argv) != 2:
    print(
        "\n".join([
            "Unpacking requires exactly 1 argument, the root directory to unpack from.",
            "The call should look like 'python src/unpack.py raw_content/Animals'.",
            "Also make sure to delimit spaces with backslashes."
        ])
    )
    exit()

rootDirectory = sys.argv[1]
print(f"Unpacking {rootDirectory}")

filenames = File.getNames(rootDirectory)

# dirs = File.getDirectories(r"output")
# Graphics.displayAll(dirs[0])
# exit()

from utils.input import Input
# print("\n".join(allFiles))

print(f"{len(filenames)} Files")

for filename in filenames:
    # img = Image.open(allFiles[0])
    image = File.getImage(filename)
    sheet = Sheet.initial(filename)

    sampleOutput = sheet.getSubpath(0)
    if File.exists(sampleOutput):
        print(f"Skipping {filename}...")
        continue

    def display():
        sheet.drawOn(image)
        print(f"current state for {sheet.filename}")

    display()

    done = False
    while not done:
        command = input(" ~> ")
        words = command.split(" ")

        choice = words[0]

        if choice == 'r':
            sheet = Sheet.initial(filename)
            display()
            print("Reset.")
        elif choice == "m":
            if len(words) != 3:
                print("Merge must have two arguments.")
                continue

            i1 = int(words[1]) if words[1].isdecimal() else None
            i2 = int(words[2]) if words[2].isdecimal() else None
            
            if i1 == None or i2 == None:
                print("Merge's arguments must be integers.")
                continue

            sheet = sheet.merge(i1, i2)
            display()
        elif choice == "d":
            if len(words) != 4:
                print("Divide requires 3 arguments.")
                continue

            i = int(words[1]) if words[1].isdecimal() else None
            w = int(words[2]) if words[2].isdecimal() else None
            h = int(words[3]) if words[3].isdecimal() else None
            if i == None or w == None or h == None:
                print("All arguments must be integers.")
                continue

            sheet = sheet.slice(i, w, h)
            display()
        elif choice == 'c':
            if len(words) != 4:
                print("Cut requires 3 arguments.")
                continue

            index = int(words[1]) if words[1].isdecimal() else None
            axis = words[2]
            pixels = int(words[3]) if words[3].isdecimal() else None
            if index == None or pixels == None or not (axis == 'x' or axis == 'y'):
                print("Invalid arguments.")

            sheet = sheet.cut(index, axis, pixels)
            display()
        elif choice == 'z':
            if len(words) == 1:
                sheet.drawOn(image)
                print("reset zoom.")
                continue

            if len(words) != 2:
                print("Zoom requires 0 or 1 arguments.")
                continue

            i = int(words[1]) if words[1].isdecimal() else None
            if i == None:
                print("index must be an integer.")
                continue
    
            subimage = sheet.getSubimage(i)
            File.displayImage(Graphics.scale(subimage, 8))
            print(f"Zooming cell #{i}")
        elif choice == 'done':
            sheet.save()
            done = True
        elif choice == 's':
            done = True
        elif choice == 'undo':
            print("Not yet implemented...")
        else:
            # print help text for babies...
            print(
                "\n".join([
                    "Enter one of the following commands:",
                    "+--------+-------------",
                    "| Divide | d $index $width $height",
                    "| Cut    | c $index $direction='x'|'y' $pixels",
                    "| Merge  | m $index1 $index2",
                    "| Zoom   | z $index | z",
                    "| Done   | done", # saves the current division.
                    "| Skip   | s ",
                    "| Reset  | r ",
                    "+--------+-------------",
                ])
            )

        