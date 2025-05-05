# Import module
from termcolor import colored
from utils.graphics import Graphics
from utils.program import Arg, Command, Program
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

# print("\n".join(allFiles))

print(f"{len(filenames)} Files")

def setSheet(newSheet):
    global sheet, previousSheet
    previousSheet = sheet
    sheet = newSheet

def display(caption):
    with File.getImage(filename) as image:
        sheet.drawOn(image)
    print(caption)
    print(f"current state for {sheet.filename}")

fileIndex = 0

def setFilename(index):
    global sheet, previousSheet, filename, filenames, fileIndex
    if index == len(filenames):
        Program.printSpecial("Done! Byyyeee")
        exit()

    fileIndex = index
    filename = filenames[index]
    # img = Image.open(allFiles[0])
    sheet = Sheet.initial(filename)
    previousSheet = None
    sampleOutput = sheet.getSubpath(0)
    if File.exists(sampleOutput):
        print(f"Skipping {filename}...")
        next()
        return
    display("Initial")

def next():
    setFilename(fileIndex+1)

def done(args):
    global sheet
    sheet.save()
    next()
doneCommand = Command(
    "done",
    "Done",
    "Save current sheet configuration",
    [],
    done,
)

def skip(args):
    next()
skipCommand = Command("s", "Skip", "Skip to the next sheet.", [], skip)

def reset(args):
    global filename
    setSheet(
        Sheet.initial(filename)
    )
    display("Reset.")
resetCommand = Command(
    "r",
    "Reset Sheet",
    "Reset the current work on this sheet.",
    [],
    reset,
)

def merge(args):
    index1 = args["index1"]
    index2 = args["index2"]

    setSheet(
        sheet.merge(index1, index2)
    )
    display(f"Merged {index1} and {index2}.")
mergeCommand = Command(
    "m",
    "Merge Boxes",
    "Merge two boxes by index. Replaces everything underneath with their bounding box.",
    [ Arg.intType("index1"), Arg.intType("index2")],
    merge
)

def divide(args):
    index = args["index"]
    numX = args["numX"]
    numY = args["numY"]

    setSheet(
        sheet.getSliced(index, numX, numY)
    )
    display(f"Sliced {index} into {numX}x{numY} sprites")
divideCommand = Command(
    "d",
    "Divide",
    "Divide a box into numX x numY subsprites. Works best if sizes are divisible.",
    [ Arg.intType("index"), Arg.intType("numX"), Arg.intType("numY") ],
    divide,
)

def divisorsOf(args):
    index = args["index"]

    sprite = sheet.subsprites[index]
    width = sprite.width
    height = sprite.height
    xDivisors, yDivisors = sprite.getDivisors()
    xDivisorStrings = [f"{div}" for div in xDivisors]
    yDivisorStrings = [f"{div}" for div in yDivisors]
    print(
        "\n".join([
            f"Width  {str(width).rjust(4)} | {colored(" ".join(xDivisorStrings), "blue")}",
            f"Height {str(height).rjust(4)} | {colored(" ".join(yDivisorStrings), "blue")}",
        ])
    )
divisorsCommand = Command(
    "divs",
    "List Divisors",
    "Lists the divisors of a box's size.",
    [ Arg.intType("index") ],
    divisorsOf,
)

def cut(args):
    global sheet
    axis = args["axis"]
    index = args["index"]
    pixels = args["pixels"]
    setSheet(sheet.getCut(index, axis, pixels))
    display(f"Cut {index} with {axis}={pixels}")
cutCommand = Command(
    "c",
    "Cut",
    "Cut a sprite at a relative x or y coordinate.",
    [ 
        Arg.enumType("axis", ['x', 'y']), 
        Arg.intType("index"), 
        Arg.intType("pixels"),
    ],
    cut,
)

def shift(args):
    global sheet
    side = args["side"]
    index = args["index"]
    pixels = args["pixels"]
    
    setSheet(
        sheet.getShifted(index, side, pixels)
    )
    display(f"Shifted {index} on {side} by {pixels}px")
shiftCommand = Command(
    "sh",
    "Shift",
    "Expand a box on a side (l/t/r/b)",
    [ 
        Arg.enumType("side", ['l', 't', 'r', 'b']), 
        Arg.intType("index"), 
        Arg.intType("pixels"),
    ],
    shift
)

def undo(args):
    setSheet(previousSheet)
    display(f"Undid previous operation.")
undoCommand = Command(
    "u",
    "Undo",
    "Undo the previous action. Only one action is stored.",
    [],
    undo,
)

def zoom(args):
    index = args["index"]
    if index == None:
        display("Reset zoom.")
        return

    subimage = sheet.getSubimage(index)
    File.displayImage(Graphics.scale(subimage, 8))
    print(f"Zooming cell #{index}")
zoomCommand = Command(
    "z",
    "Zoom",
    "Zoom onto a specific subsprite, or reset if no index is passed",
    [ Arg.intType("index").optional() ],
    zoom,
)

def init():
    setFilename(0)
    Program.printSuccess("Initialized :)")

Program(
    "Unpacker",
    init,
    [ 
        mergeCommand,
        divideCommand,
        cutCommand,
        shiftCommand,

        divisorsCommand,
        zoomCommand,
        
        undoCommand,
        
        resetCommand,
        skipCommand,
        doneCommand,
    ],
).run()
