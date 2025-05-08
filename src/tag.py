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

manifest = Manifest.load()
previousManifest = Manifest.load()

def setManifest(newManifest):
    global manifest, previousManifest
    previousManifest = manifest
    manifest = newManifest
    manifest.save()

pageSize = 32

pages = []
currentPageIndex = 0

def step(count, caption=None):
    global currentPageIndex, currentPage
    currentPageIndex = currentPageIndex + count
    if currentPageIndex < 0:
        currentPageIndex = 0
    if currentPageIndex >= len(pages):
        currentPageIndex = len(pages)-1
    currentPage = pages[currentPageIndex]
    messages = []
    if caption is not None: messages.append(caption)
    if count is not 0: messages.append(f"Stepped by {count}.")
    displayPage("\n".join(messages))

def recalculate(caption=None):
    global pages, allFiles
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
    step(0, caption=caption)

def filenameByIndex(index):
    matches = [
        filename for filename in currentPage
        if f"/{index}.png" in filename
    ]
    if len(matches) == 0: return None
    if len(matches) > 1: raise LookupError(f"Fatal: Too many files at index={index}! {matches}")
    return matches[0]

def display(list, caption):
    File.displayList(list, manifest, caption=caption)

def displayPage(caption):
    global currentPageIndex, pages, currentPage
    global manifest, previousManifest
    directory = "/".join(currentPage[0].split("/")[:-1])
    display(
        currentPage,
        f"Current: {currentPageIndex+1}/{len(pages)}, {directory}\n{caption}",
    )

def tagFunction(args):
    global currentPage, manifest
    indices = args["indices"]
    filenames = [ filenameByIndex(index) for index in indices ]
    if len(filenames) == 0: filenames = currentPage
    newTags = args["tags"]
    newManifest = manifest.withTags(filenames, newTags)
    setManifest(newManifest)
    displayPage(f"Tagged {filenames} with each of {newTags}.")
tagCommand = Command(
    "t", "Tag",
    "\n".join([
        "idempotently add one or more tags to the specified images.\n\nTags the entire page if no indices are specified.",
    ]),
    [ Arg.intType("indices").variable(), Arg.stringType("tags").variable() ],
    tagFunction,
)

def untag(args):
    global currentPage, manifest
    indices = args["indices"]
    filenames = [ filenameByIndex(index) for index in indices ]
    if len(filenames) == 0: filenames = currentPage
    tagsToRemove = args["tags"]
    newManifest = manifest.withoutTags(filenames, tagsToRemove)
    setManifest(newManifest)
    displayPage(f"Untagged {filenames} with each of {tagsToRemove}")
untagCommand = Command(
    "ut", "Untag",
    "Idempotently remove tags from the selected files.\n\nIndex system works the same as the t command's.",
    [ Arg.intType("indices").variable(), Arg.stringType("tags").variable() ],
    untag,
)

def tagRange(args):
    global manifest
    indices = args["ranges"]
    if len(indices)%2 != 0: raise ValueError("An even number of indices must be provided.")
    newTags = args["tags"]
    newManifest = Manifest.load()
    pairs = []
    for i in range(int(len(indices)/2)):
        start = indices[i*2]
        end = indices[i*2 + 1]
        filenames = [ filenameByIndex(index) for index in range(start, end+1) ]
        newManifest = newManifest.withTags(filenames, newTags)
        pairs.append([start, end])
    setManifest(newManifest)
    displayPage(f"Tagged ranges {pairs} with each of {newTags}")
tagRangeCommand = Command(
    "tr", "Tag Range",
    "adds tags to all images in inclusive ranges.",
    [ Arg.intType("ranges").variable(), Arg.stringType("tags").variable() ],
    tagRange,
)

def untagRange(args):
    global manifest
    indices = args["ranges"]
    if len(indices)%2 != 0: raise ValueError("An even number of indices must be provided.")
    tagsToRemove = args["tags"]
    newManifest = Manifest.load()
    pairs = []
    for i in range(int(len(indices)/2)):
        start = indices[i*2]
        end = indices[i*2 + 1]
        filenames = [ filenameByIndex(index) for index in range(start, end+1) ]
        newManifest = newManifest.withTags(filenames, tagsToRemove)
        pairs.append([start, end])
    setManifest(newManifest)
    displayPage(f"Untagged ranges {pairs} with each of {tagsToRemove}")
untagRangeCommand = Command(
    "utr", "Untag Range",
    "adds tags to all images in an inclusive range.",
    [ Arg.intType("ranges").variable(), Arg.stringType("tags").variable() ],
    untagRange,
)

def removeFile(args):
    global previousManifest
    filenames = args["filenames"]
    for filename in filenames:
        filename = filenameByIndex(filename)
        File.deleteFile(filename)
        preivousManifest = None
        recalculate(caption=f"Deleted {filename}")
removeFileCommand = Command(
    "rm", "Remove",
    "Deletes image files by their index.",
    [ Arg.stringType("filenames").variable() ],
    removeFile
)

def stepFunction(args):
    global previousManifest
    count = args["count"]
    if count is None: count = 1

    if (count > 0 and currentPageIndex == len(pages)-1) or (count < 0 and currentPageIndex == 0):
        raise ValueError("No more in that direction.")
    previousManifest = None

    step(count)
stepCommand = Command(
    "s", "Step",
    "Step forwards or backwards through the pages. Defaults to count=1",
    [ Arg.intType("count").optional() ],
    stepFunction
)

def undo(args):
    global previousManifest
    if previousManifest == None:
        raise ValueError("The previous action isn't possible to undo.")
    setManifest(previousManifest)
    displayPage("Undid previous action.")
undoCommand = Command(
    "u", "Undo",
    "Undo a single action.",
    [],
    undo,
)

def init():
    recalculate()
    
Program(
    "Tagger",
    init,
    [
        tagCommand,
        tagRangeCommand,

        untagCommand,
        untagRangeCommand,

        stepCommand,
        removeFileCommand,
        undoCommand,
    ],
).run()
