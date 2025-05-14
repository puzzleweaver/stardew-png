# Import module
from termcolor import colored
from utils.graphics import Graphics
from utils.input import Input
from utils.program import Arg, Command, Program
from utils.program_exception import ProgramException
from utils.sheet import Box, Sheet
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
if len(filenames) == 0:
    Program.printError(f"No suitable png files in {rootDirectory}...")
    exit()

print(f"{len(filenames)} Files")

def getOutputFiles():
    return File.getOutputFiles(sheet.filename)

def isDone():
    return File.isUnpacked(sheet.filename)

def isNotDoneValidation():
    if isDone():
        raise ProgramException("Invalid state for that operation.")
    
def setSheet(newSheet):
    global sheet, previousSheet
    previousSheet = sheet
    sheet = newSheet

def display(caption=None):
    
    if isDone():
        outputFiles = getOutputFiles()
        File.displayAll(outputFiles)
        print(f"{fileIndex+1}/{len(filenames)} {sheet.filename}")
        hasProgress = File.hasUnpackingProgress(filename)
        if hasProgress:
            Program.printSpecial("If you redo from here, you will NOT have to redo everything.")
        else:
            Program.printSpecial("WARNING: redo from here will clear all work on this sheet!!!")
        return
    
    with File.getImage(filename) as image:
        sheet.drawOn(image, viewport)
    if caption is not None:
        print(caption)
    print(f"{fileIndex+1}/{len(filenames)} {sheet.filename}")

fileIndex = 0

def setViewport(newViewport):
    global viewport
    viewport = newViewport
def resetViewport():
    with File.getImage(filename) as image:
        setViewport(Box(0, 0, image.width, image.height))

def setFilename(index, show=True):
    global sheet, previousSheet, filename, filenames, fileIndex

    fileIndex = index
    filename = filenames[index]
    resetViewport()
    # img = Image.open(allFiles[0])
    sheet = Sheet.initial(filename)
    previousSheet = None

    caption = None

    # see if there was already work here
    outputDirectory = sheet.getDirectory()
    progressFilename = f"{outputDirectory}/progress.json"
    if File.exists(progressFilename):
        sheet = Sheet.fromData(File.readJson(progressFilename))
        caption = "Loaded from progress.json."
    
    display(caption)

def step(count):
    newIndex = fileIndex+count
    maxIndex = len(filenames)-1

    # catch no op cases
    if fileIndex == 0 and count < 0:
        Program.printError("Already at beginning.")
        return
    if fileIndex == maxIndex and count > 0:
        Program.printSpecial("All Done :?")
        exit()
        
    # clamp
    if newIndex < 0: newIndex = 0
    if newIndex > maxIndex: newIndex = maxIndex

    setFilename(newIndex)

def save(args):
    File.writeJson(
        f"{sheet.getDirectory()}/progress.json",
        sheet.toData(),
    )
    Program.printSpecial("Backed up progress.")
saveCommand = Command(
    "save",
    "Save Progress",
    "Save your work so far. The saved state is used whenever you come back to this sheet, on subsequent runs of the program or via page navigation.",
    [],
    save,
    validation=isNotDoneValidation,
)

def done(args):
    global sheet
    save({})
    sheet.saveFinalImages()
    display("Saved output.")
doneCommand = Command(
    "done",
    "Done",
    "Save the individual sprites and mark this sheet as 'Done', so that it is skipped in subsequent runs.",
    [],
    done,
    validation=isNotDoneValidation,
)

def redo(args):
    outputFiles = getOutputFiles()
    for file in outputFiles:
        File.deleteFile(file, confirm=False)
    display("Unfinalized!")
redoCommand = Command(
    "redo",
    "Redo Unpacking",
    "Delete the sliced images and set the image in a 'progress saved but not finalized' state so you can edit the unpacking",
    [],
    redo,
)

def stepFunction(args):
    count = args["count"]
    if count == None: count = 1
    step(count)
stepCommand = Command(
    "s",
    "Step",
    "Step some number of files forward or backwards, defauts to one step forwards.",
    [ Arg.intType("count").optional() ],
    stepFunction,
)

def reset(args):
    global filename
    setSheet(
        Sheet.initial(filename)
    )
    resetViewport()
    display("Reset.")
resetCommand = Command(
    "r",
    "Reset Sheet",
    "Reset the current work on this sheet.",
    [],
    reset,
    validation=isNotDoneValidation,
)

def merge(args):
    indices = args["indices"]
    
    if len(indices)%2 == 1:
        raise ProgramException("Merge requires an even number of indices.")

    newSheet = sheet
    pairs = []
    for i in range(int(len(indices)/2)):
        index1 = indices[i*2]
        index2 = indices[i*2 + 1]
        newSheet = newSheet.merge(index1, index2)
        pairs.append([index1, index2])
    setSheet(newSheet)
    display(f"Merged Pairs: {pairs}")
mergeCommand = Command(
    "m",
    "Merge Boxes",
    "Merge pairs of boxes by index. Replaces everything underneath with the bounding box.",
    [ Arg.intType("indices").variable() ],
    merge,
    validation=isNotDoneValidation,
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
    validation=isNotDoneValidation,
)

def divisorsOf(args):
    index = args["index"]

    sprite = sheet.boxes[index]
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
    validation=isNotDoneValidation,
)

def cut(args):
    global sheet
    side = args["side"]
    indices = args["indices"]
    pixels = args["pixels"]
    newSheet = sheet
    for index in indices:
        newSheet = newSheet.getCut(index, side, pixels)
    setSheet(newSheet)
    display(f"Cut {index} with {side}={pixels}")
cutCommand = Command(
    "c",
    "Cut",
    "Cut a sprite at a coordinate relative to one of its edges.",
    [
        Arg.intType("indices").variable(),
        Arg.enumType("side", ['l', 't', 'r', 'b']), 
        Arg.intType("pixels"),
    ],
    cut,
    validation=isNotDoneValidation,
)

def shift(args):
    global sheet
    side = args["side"]
    indices = args["indices"]
    pixels = args["pixels"]
    
    newSheet = sheet
    for index in indices:
        newSheet = newSheet.getShifted(index, side, pixels)
    setSheet(newSheet)
    display(f"Shifted {index} on {side} by {pixels}px")
shiftCommand = Command(
    "sh",
    "Shift",
    "Expand a box on one side.\nMay result in overlapping or disjointed boxes",
    [ 
        Arg.intType("indices").variable(),
        Arg.enumType("side", ['l', 't', 'r', 'b']), 
        Arg.intType("pixels"),
    ],
    shift,
    validation=isNotDoneValidation,
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
    validation=isNotDoneValidation,
)

def zoom(args):
    global viewport
    indices = args["indices"]
    if indices == []:
        resetViewport()
        display("Reset zoom.")
        return
    setViewport(sheet.getBounds(indices))
    display(f"Zoomed to show all of {indices}")
zoomCommand = Command(
    "z",
    "Zoom",
    "Zoom to show one or more boxes, or reset viewport if no indices are given.",
    [ Arg.intType("indices").variable() ],
    zoom,
    validation=isNotDoneValidation,
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
        stepCommand,
        saveCommand,
        doneCommand,
        redoCommand,
    ],
).run()
