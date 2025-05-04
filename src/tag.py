# Import module
from math import ceil
import sys
from utils.file import File
from utils.manifest import Manifest
from utils.program import Arg, Command, Program

File.setImageHeight(40)

if len(sys.argv) != 2:
    print(
        "\n".join([
            "Unpacking requires exactly 1 argument, the output directory to tag things in.",
            "The call should look like 'python src/tag.py output/Animals'.",
            "Also make sure to delimit spaces with backslashes."
        ])
    )
    exit()

rootDirectory = sys.argv[1]
print(f"Tagging {rootDirectory}")
dirs = File.getDirectories(rootDirectory)

def getManifest():
    return Manifest.fromJson(
        File.readText("output/manifest.json", "{}")
    )

# allTags = getManifest().getAllTags()
# print(allTags)
# exit()

pageSize = 32

pages = []
currentPageIndex = 0

def step(count):
    global currentPageIndex, currentPage, selected
    currentPageIndex = currentPageIndex + count
    if currentPageIndex < 0:
        currentPageIndex = 0
    if currentPageIndex >= len(pages):
        currentPageIndex = len(pages)-1
    currentPage = pages[currentPageIndex]
    selected = currentPage
    displayPage()

def recalculate():
    global pages
    pages = []
    for directory in dirs:

        allFiles = File.getNames(directory)
        allFiles.sort(key=lambda filename: int(File.getIndex(filename)))

        subpages = ceil(len(allFiles)/pageSize)
        for i in range(subpages):
            pages.append(
                allFiles[i*pageSize : (i+1)*pageSize]
            )

    # freshly clamp page index
    step(0)

def filenameByIndex(index):
    global currentPage
    matches = [
        filename for filename in currentPage
        if f"/{index}.png" in filename
    ]
    if len(matches) == 0: return None
    if len(matches) > 1: raise LookupError(f"Fatal: Too many files at index={index}! {matches}")
    return matches[0]

def display(list, caption):
    global selected
    File.displayList(list, getManifest(), selected=selected, caption=caption)

def displayPage():
    global currentPageIndex, pages, currentPage
    directory = "/".join(currentPage[0].split("/")[:-1])
    display(
        currentPage,
        f"Current: {currentPageIndex+1}/{len(pages)}, {directory}",
    )

def previous(args):
    global currentPageIndex
    if currentPageIndex == 0:
        Program.printWarning("Already at beginning.")
        return
    
    count = args["count"]
    if count is None: count = 1
    step(-count)
previousCommand = Command(
    "p", "Previous",
    "navigates backwards 1 or more pages",
    [ Arg.intType("count").optional() ],
    previous
)

def deselect(args):
    global selected, currentPage
    indices = args["indices"]

    if len(indices) == 0:
        selected = []
    else:
        excludedFilenames = [
            filenameByIndex(index) for index in indices
        ]
        selected = [
            filename for filename in selected
            if filename not in excludedFilenames
        ]
    displayPage()
deselectCommand = Command(
    "d", "Deselect",
    "idempotently deselect by index, deselects all when no indices are specified",
    [ Arg.stringType("indices").variable() ],
    deselect
)

def select(args):
    global selected, currentPage
    indices = args["indices"]

    if len(indices) == 0:
        selected = currentPage
    else:
        selected.extend([
            file for file in [
                filenameByIndex(arg) for arg in indices
            ]
            if file in currentPage
        ])
    displayPage()
selectCommand = Command(
    "s", "Select",
    "Select one or more indices, selects all when no index is specified",
    [ Arg.intType("indices").variable() ],
    select
)

def selectRange(args):
    global selected, currentPage
    start = args["start"]
    end = args["end"]
    indices = range(start, end+1)

    selected.extend([
        file for file in [
            filenameByIndex(arg) for arg in indices
        ]
        if file in currentPage
    ])
    displayPage()
selectRangeCommand = Command(
    "sr", "Select Range",
    "Select all indices in an inclusive interval",
    [ Arg.intType("start"), Arg.intType("end") ],
    selectRange
)

def deselectRange(args):
    global selected, currentPage
    start = args['start']
    end = args['end']
    indices = range(start, end+1)

    excludedFilenames = [
        filenameByIndex(index) for index in indices
    ]
    selected = [
        filename for filename in selected
        if filename not in excludedFilenames
    ]
    displayPage()
deselectRangeCommand = Command(
    "dr", "Deselect Range",
    "Deselect all indices in an inclusive interval",
    [ Arg.intType("start"), Arg.intType("end") ],
    deselectRange
)

def addTags(args):
    global selected
    if len(selected) == 0:
        Program.printError("Nothing selected.")
        return

    newTags = args["tags"]
    if len(newTags) == 0:
        Program.printError("No tags specified")
        return
    
    newManifest = getManifest().withTagsAdded(selected, newTags)
    File.writeText("output/manifest.json", newManifest.toJson())
    displayPage()
addTagsCommand = Command(
    "t", "Tag",
    "idempotently add one or more tags to all selected files",
    [ Arg.stringType("tags").variable() ],
    addTags
)

def removeTags(args):
    if len(selected) == 0:
        Program.printError("Nothing selected.")
        return

    tagsToRemove = args["tags"]
    newManifest = getManifest().withTagsRemoved(selected, tagsToRemove)
    File.writeText("output/manifest.json", newManifest.toJson())
    displayPage()
removeTagsCommand = Command(
    "ut", "UnTag",
    "idempotently remove tags from the selected files",
    [ Arg.stringType("tags").variable() ],
    removeTags
)

def removeFile(args):
    filenames = args["filenames"]
    for filename in filenames:
        filename = filenameByIndex(filename)
        File.displayImageFile(filename)
        confirmation = input(f"Delete {filename}? (Y to confirm)")
        if(confirmation == "Y"):
            File.deleteFile(filename)
        else:
            print(f"Skipping {filename}.")
    recalculate()
    displayPage()
removeFileCommand = Command(
    "rm", "Remove",
    "Deletes image files by their index.",
    [ Arg.stringType("filenames").variable() ],
    removeFile
)

def continueFunction(args):
    if currentPageIndex == len(pages)-1:
        Program.printWarning("Already at end.")
        return

    count = args["count"]
    if count is None: count = 1
    step(count)
continueCommand = Command(
    "c", "Continue",
    "navigate forwards 1 or more pages",
    [ Arg.intType("count").optional()],
    continueFunction
)

def init():
    recalculate()
    
Program(
    "Tagger",
    init,
    [
        addTagsCommand,
        removeTagsCommand,

        selectCommand,
        selectRangeCommand,
        deselectCommand,
        deselectRangeCommand,

        continueCommand,
        previousCommand,

        removeFileCommand,
    ],
).run()
