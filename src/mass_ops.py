# Import module
import json
from string import ascii_lowercase
import traceback

from termcolor import colored
from utils.file import File
from utils.graphics import Graphics
from utils.global_tags import GlobalTags
from utils.local_tags import LocalTags
from utils.program import Arg, Command, Program

File.setImageHeight(40)

def recalculate():
    global globalTags
    globalTags = GlobalTags.load()

# Which
def which(args):
    tags = args["tags"]

    filesWithTag = globalTags.getFilesWithTags(tags)
    filesWithTag.sort()
    
    File.displayList(
        filesWithTag,
        [" ".join(globalTags.getFileTags(file)) for file in filesWithTag],
        caption=f"Everything tagged '{' '.join(tags)}' ({len(filesWithTag)})"
    )
whichCommand = Command(
    "show", "Show Files",
    "Show all files with a tag",
    [ Arg.stringType("tags").variable() ],
    which,
)

# Remove Tags
def rmtag(args):
    tagsToRemove = args["tags"]
    for localTags in LocalTags.getAll():
        newLocalTags = localTags.withoutTags(tagsToRemove)
        newLocalTags.save()
rmtagCommand = Command(
    "rmtag", "Remove Tag",
    "Remove a tag everywhere it appears.",
    [ Arg.stringType("tags").variable() ],
    rmtag
)

def crop(args):
    # TODO iterate over all output files, crop each image.
    outputFiles = File.getNames("output")
    for file in outputFiles:
        image = File.getImage(file)
        cropped = Graphics.crop(image)
        if cropped is not None: 
            File.saveImage(file, cropped)
        else:
            File.deleteFile(file, confirm=False)
    Program.printSpecial("Done cropping everything :3")
cropCommand = Command(
    "crop", "Crop All Images",
    "Iterate over each image in the output directory, either resave a cropped copy of it, or delete it if it's only transparent.",
    [],
    crop,
)

# # Clean Manifest
# def clean(args):
#     newManifest, removed = GlobalTags.load().clean()
#     newManifest.save()
#     print(f"Removed tags from manifest: {' '.join(removed)}")
# cleanCommand = Command(
#     "clean", "Clean Manifest",
#     "Removes all nonexistant files from the manifest.",
#     [],
#     clean,
# )

# List Tags
def list(args):
    globalTags = GlobalTags.load()
    allTags = globalTags.getAllTags()
    allTags.sort()

    count = len(allTags)
    Program.clear()
    print(f"Total Tags: {count}")

    toggle = False
    for c in ascii_lowercase:
        tagsWithC = [
            tag for tag in allTags
            if len(tag) > 0 and tag[0] == c
        ]
        if len(tagsWithC) == 0: continue
        tagsWithC.sort()
        tagsString = ""
        col = "blue"
        if toggle: col = "black"
        tagsString += colored(
            " ".join([
                f"{tag}({len(globalTags.getFilesWithTag(tag))})"
                for tag in tagsWithC
            ]),
            col,
        )
        toggle = not toggle
        print(colored(f"{c.upper()}: {tagsString}", col))
listCommand = Command(
    "list", "List Tags",
    "List all tags.",
    [],
    list,
)

def exportFunction(args):
    Program.printSpecial("Exporting...")
    
    # delete existing exported/ directory
    File.deleteDirectory("exported")

    # make sure the folders involved are created...
    File.ensureFolderExists("exported/sprites/")
    File.ensureFolderExists("exported/tags/")
    
    # create exported/sprites/ directory and copy the entire output/ folder into it
    # TODO only copy the image files over.
    File.copyDirectory("output/", "exported/sprites/")

    # create files:
    globalTags: GlobalTags = GlobalTags.load()

    #  exported/all_tags.json: lists all tags on any image.
    allTags = globalTags.getAllTags()
    File.writeJson("exported/all_tags.json", allTags)

    # helper function for transforming the manifest's filenames so that things work right
    def correct(filename: str):
        return "/".join(filename.split("/")[1:])

    #  exported/tags/<tag>.json: lists all files associated with the tag.
    for tag in allTags:
        filesWithTag = globalTags.getFilesWithTag(tag)
        filesWithTag = [
            correct(filename) for filename in filesWithTag
        ]
        sharedTags = globalTags.getSharedTags(tag)
        File.writeJson(
            f"exported/tags/{tag}.json",
            {
                "files": filesWithTag,
                "shared": sharedTags,
            },
        )

    #  exported/sprites/<sprite path>/<index>_tags.json: lists all tags on the corresponding image.
    files = [ correct(filename) for filename in File.getNames("output") ]
    for file in files:
        tagFilename = f"exported/sprites/{file}".replace(".png", "_tags.json")
        fileTags = globalTags.getFileTags(f"output/{file}")
        File.writeJson(tagFilename, fileTags)

    Program.printSpecial("Donezo :3")

exportCommand = Command(
    "export", "Export Manifest",
    "Export the manifest in a format which is consumable for the frontend.",
    [],
    exportFunction,
)

Program(
    "Mass Tagger",
    recalculate,
    [ 
        # tag commands
        rmtagCommand,
        listCommand, 
        whichCommand,
        
        # cleanup commands
        cropCommand,
        
        # export!
        exportCommand,
    ],
).run()