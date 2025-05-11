# Import module
from string import ascii_lowercase

from termcolor import colored
from utils.file import File
from utils.graphics import Graphics
from utils.global_tags import GlobalTags
from utils.local_tags import LocalTags
from utils.program import Arg, Command, Program

File.setImageHeight(40)

# Which
def show(args):
    tags = args["tags"]

    globalTags = GlobalTags.load()

    files = globalTags.query(tags)
    files.sort()
    
    File.displayAllWithCaptions(
        files,
        [
            File.transformPath(file, lambda words: words[:-2])
            for file in files
        ],
        aspectRatio=0.8,
        caption=f"Everything matching '{' '.join(tags)}' ({len(files)}):"
    )
showCommand = Command(
    "show", "Show Files",
    "Show all files with a tag",
    [ Arg.stringType("tags").variable() ],
    show,
)

# Remove Tags
def rmtags(args):
    tagsToRemove = args["tags"]
    for localTags in LocalTags.getAll():
        localTags.withoutTags(
            localTags.getIndices(), 
            tagsToRemove,
        ).save()
rmtagCommand = Command(
    "rmtag", "Remove Tag",
    "Remove a tag everywhere it appears.",
    [ Arg.stringType("tags").variable() ],
    rmtags
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
def clean(args):
    Program.printSpecial("Removing empty tag...")
    rmtags({ "tags": [''] })
    Program.printSpecial("Done.")

    for localTags in LocalTags.getAll():
        newLocalTags = localTags
        for index in localTags.getIndices():
            file = f"{localTags.directory}/{index}.png"
            if not File.exists(file):
                newLocalTags= newLocalTags.withoutIndex(index)
                print(f"Deleted {file}.")
        newLocalTags.save()

cleanCommand = Command(
    "clean", "Clean Manifest",
    "Removes all nonexistant files from the manifest.",
    [],
    clean,
)

# List Tags
def list(args):
    argTags = args["tags"]

    globalTags = GlobalTags.load()
    tags = globalTags.getAllTags()
    tags.sort()

    count = len(tags)
    Program.clear()
    print(f"Total Tags: {count}")

    toggle = False
    for c in ascii_lowercase:
        tagsWithC = [
            tag for tag in tags
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
    [ Arg.stringType("tags").variable() ],
    list,
)

def progressFunction(args):
    area = args["area"]

    if area == "tagging":
        globalTags = GlobalTags.load()

        filenames = File.getNames("raw_content")
        subdirectories = {
            "/".join(name.split("/")[:2])
            for name in filenames
        }

        def getProgress(name):
            if File.isUnpacked(name): return 2
            elif File.hasUnpackingProgress(name): return 1
            else: return 0
            
        for subdirectory in subdirectories:
            subfilenames = File.getNames(subdirectory)
            output = ""
            Program.printSpecial(subdirectory)
            for i in range(len(subfilenames)):
                outputDir = File.getOutputDirectory(subfilenames[i])

                color = "red"
                goodFiles = 0
                badFiles = 0
                for outputFile in File.getNames(outputDir):
                    if len(globalTags.getFileTags(outputFile)) == 0:
                        badFiles += 1
                    else: goodFiles += 1

                if goodFiles == 0 and badFiles == 0:
                    continue

                color = "green"
                if badFiles == 0: color = "green"
                elif goodFiles > badFiles: color = "yellow"
                else: color = "red"
                output += colored(
                    "/".join(outputDir.split("/")[2:]) + f"({goodFiles}/{goodFiles+badFiles})",  
                    color
                ) + " "
            print(output)
            print()

    if area == "unpacking":
        filenames = File.getNames("raw_content")
        subdirectories = {
            "/".join(name.split("/")[:2])
            for name in filenames
        }
        
        def getProgress(name):
            if File.isUnpacked(name): return 2
            elif File.hasUnpackingProgress(name): return 1
            else: return 0
            
        for subdirectory in subdirectories:
            subfilenames = File.getNames(subdirectory)
            output = ""
            Program.printSpecial(subdirectory)
            for i in range(len(subfilenames)):
                color = "black"
                filename = subfilenames[i]
                progress = getProgress(filename)
                if progress == 0: color = "red"
                if progress == 1: color = "yellow"
                if progress == 2: color = "green"
                output += colored(
                    "/".join(filename.split("/")[-1:]).replace(".png", ""),
                    color
                ) + " "
            print(output)
            print()
progressCommand = Command(
    "progress",
    "Progress Overview",
    "Show information on what has been done for which files.",
    [ Arg.enumType("area", ["unpacking", "tagging"]) ],
    progressFunction,
)

def exportFunction(args):
    Program.printSpecial("Exporting...")
    
    # delete existing exported/ directory
    File.deleteDirectory("exported")

    # make sure the folders involved are created...
    File.ensureFolderExists("exported/sprites/")
    File.ensureFolderExists("exported/tags/")
    
    # create exported/sprites/ directory and copy the entire output/ folder into it
    files = File.getNames("output")
    File.copyDirectory("output/", "exported/sprites/")
    directories = File.getDirectories("exported/sprites")
    for directory in directories:
        File.deleteFile(f"{directory}/tags.json", confirm=False)
        File.deleteFile(f"{directory}/progress.json", confirm=False)

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
        tagFilename = f"exported/sprites/{file}".replace(".png", "t.json")
        fileTags = globalTags.getFileTags(f"output/{file}")
        File.writeJson(tagFilename, fileTags)

    Program.printSpecial("Donezo :3")
exportCommand = Command(
    "export", "Export Manifest",
    "Export the manifest in a format which is consumable for the frontend.",
    [],
    exportFunction,
)

def init():
    print("Initialized.")

Program(
    "Mass Tagger",
    init,
    [
        # tag commands
        rmtagCommand,
        listCommand,
        showCommand,
        
        # cleanup commands
        cropCommand,
        cleanCommand,
        
        # export!
        exportCommand,
        progressCommand,
    ],
).run()