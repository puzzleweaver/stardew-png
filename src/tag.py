# Import module
from math import ceil
import sys
from utils.file import File
from utils.program import Arg, Command, Program
from utils.program_exception import ProgramException
from utils.tags import Tags

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

def setTags(newTags):
    global tags, previousTags
    previousTags = tags
    tags = newTags
    tags.save()

pageSize = 32

pages = []
currentPageIndex = 0

def step(count, caption=None):
    global currentPageIndex, currentPage, currentDirectory
    global tags, previousTags
    currentPageIndex = currentPageIndex + count
    if currentPageIndex < 0:
        currentPageIndex = 0
    if currentPageIndex >= len(pages):
        currentPageIndex = len(pages)-1
    currentPage = pages[currentPageIndex]
    currentDirectory = pageDirectories[currentPageIndex]
    previousTags = tags = Tags.load(currentDirectory)
    messages = []
    if caption is not None: messages.append(caption)
    if count is not 0: messages.append(f"Stepped by {count}.")
    displayPage("\n".join(messages))

def recalculate(caption=None):
    global pages, allFiles, pageDirectories
    pages = []
    pageDirectories = []
    for directory in dirs:

        allFiles = File.getNames(directory)
        allFiles.sort(key=lambda filename: int(File.getIndex(filename)))

        subpages = ceil(len(allFiles)/pageSize)
        for i in range(subpages):
            page = [
                int(file.split("/")[-1].split('.')[0])
                for file in allFiles[i*pageSize : (i+1)*pageSize]
            ]
            pages.append(page)
            pageDirectories.append(directory)

    # freshly clamp page index
    step(0, caption=caption)

def filenameByIndex(index):
    global currentDirectory
    return f"{currentDirectory}/{index}.png"

def display(indices, caption):
    global tags
    filenames = [ filenameByIndex(index) for index in indices ]
    captions = [ " ".join(tags.getTags(index)) for index in indices ]
    File.displayList(filenames, captions, caption=caption)

def displayPage(caption):
    global currentPageIndex, pages, currentPage, currentDirectory
    global tags, previousTags
    display(
        currentPage,
        f"Current: {currentPageIndex+1}/{len(pages)}, {currentDirectory}\n{caption}",
    )

def tagFunction(args):
    global currentPage, tags
    addedTags = args["tags"]
    indices = args["indices"]
    if len(indices) == 0: indices = currentPage

    setTags(
        tags.withTags(indices, addedTags)
    )
    displayPage(f"Tagged {indices} with each of {addedTags}.")
tagCommand = Command(
    "t", "Tag",
    "\n".join([
        "idempotently add one or more tags to the specified images.\n\nTags the entire page if no indices are specified.",
    ]),
    [ Arg.intType("indices").variable(), Arg.stringType("tags").variable() ],
    tagFunction,
)

def untag(args):
    global currentPage, tags
    tagsToRemove = args["tags"]
    indices = args["indices"]
    if len(indices) == 0: indices = currentPage

    setTags(
        tags.withoutTags(indices, tagsToRemove)
    )
    displayPage(f"Untagged {indices} with each of {tagsToRemove}")
untagCommand = Command(
    "ut", "Untag",
    "Idempotently remove tags from the selected files.\n\nIndex system works the same as the t command's.",
    [ Arg.intType("indices").variable(), Arg.stringType("tags").variable() ],
    untag,
)

def getRangeIndices(ranges: list[int]):
    if len(ranges)%2 != 0:
        raise ProgramException("Range parameters must have even lengths.")
    ret = []
    for i in range(int(len(ranges)/2)):
        start = ranges[i*2]
        end = ranges[i*2+1]
        for index in range(start, end+1):
            if index not in ret:
                ret.append(index)
    return ret

def tagRange(args):
    global tags
    addedTags = args["tags"]
    indices = getRangeIndices(args["ranges"])
    
    setTags(
        tags.withTags(indices, addedTags)
    )
    displayPage(f"Tagged indices {indices} with each of {addedTags}")
tagRangeCommand = Command(
    "tr", "Tag Range",
    "adds tags to all images in inclusive ranges.",
    [ Arg.intType("ranges").variable(), Arg.stringType("tags").variable() ],
    tagRange,
)

def untagRange(args):
    global tags
    indices = getRangeIndices(args["ranges"])
    tagsToRemove = args["tags"]
    setTags(
        tags.withoutTags(indices, tagsToRemove)
    )
    displayPage(f"Untagged indices {indices} with each of {tagsToRemove}")
untagRangeCommand = Command(
    "utr", "Untag Range",
    "adds tags to all images in an inclusive range.",
    [ Arg.intType("ranges").variable(), Arg.stringType("tags").variable() ],
    untagRange,
)

def removeFile(args):
    global previousTags, tags
    indices = args["indices"]
    for index in indices:
        filename = filenameByIndex(index)
        try:
            File.deleteFile(filename) # will throw error if no consent
            setTags(tags.withoutIndex(index))
            recalculate(caption=f"Deleted {filename}")
            previousTags = None # prevent undo, because you can't undelete the file.
        except:
            print(f"Skipping {filename}")
removeFileCommand = Command(
    "rm", "Remove",
    "Deletes image files by their index.",
    [ Arg.stringType("indices").variable() ],
    removeFile
)

def stepFunction(args):
    global previousTags
    count = args["count"]
    if count is None: count = 1

    if (count > 0 and currentPageIndex == len(pages)-1):
        Program.printSpecial('"This is the end" --Adele')
        return
    if (count < 0 and currentPageIndex == 0):
        Program.printWarning('Already at first page.')
        return
    previousTags = None

    step(count)
stepCommand = Command(
    "s", "Step",
    "Step forwards or backwards through the pages. Defaults to count=1",
    [ Arg.intType("count").optional() ],
    stepFunction
)

def undo(args):
    global previousTags
    if previousTags == None:
        raise ProgramException("The previous action isn't possible to undo.")
    setTags(previousTags)
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
