# Import module
import copy
from string import ascii_lowercase

from termcolor import colored
from utils.file import File
from utils.format_text import Prints
from utils.graphics import Graphics
from utils.global_tags import GlobalTags
from utils.input import Input
from utils.local_tags import LocalTags
from utils.program import Arg, Command, Program
from utils.program_exception import ProgramException
from utils.tagging import collect

File.setImageHeight(40)

# Which
def show(args):
    tags = args["tags"]

    globalTags = GlobalTags.load()

    files = globalTags.query(tags)
    files.sort()
    
    captions = [ file + ": \n" + " ".join(globalTags.getFileTags(file)) for file in files ]
    File.displayAllWithCaptions(
        files,
        # [
        #     File.transformPath(file, lambda words: words[:-2])
        #     for file in files
        # ]
        captions,
        caption=f"Everything matching '{' '.join(tags)}' ({len(files)}):"
    )
showCommand = Command(
    "show", "Show Files",
    "Show all files with a tag",
    [ Arg.stringType("tags").variable() ],
    show,
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
    for localTags in LocalTags.getAll():
        newLocalTags = localTags
        indices = copy.deepcopy(list(localTags.getIndices()))
        for index in indices:
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
def listFunction(args):
    globalTags = GlobalTags.load()
    tags = globalTags.getAllTags()
    tags.sort()

    count = len(tags)
    Program.clear()
    print(f"Total Tags: {count}")

    method = args["method"]
    if method == None:
        method = 'letter'

    if method == 'letter':
        by = lambda tag: tag[0]
        transform = lambda tag: f"{tag}({len(globalTags.getFilesWithTag(tag))})"

    if method == 'count':
        by = lambda tag: len(globalTags.getFilesWithTag(tag))
        transform = lambda tag: f"{tag}"

    collected = collect(tags, by, transform)
    keys = list(collected.keys())
    keys.sort()
    lines = [ f"\n---{f'{key}'.upper()}({len(collected[key])})---\n{' '.join(collected[key])}" for key in keys]
    Prints.stripes(lines)
listCommand = Command(
    "list", "List Tags",
    "List all tags.",
    [ Arg.enumType("method", ["letter", "count"]).optional() ],
    listFunction,
)

def refactor(args):
    allTags = args["tags"]
    selectors = [
        tag[1:] for tag in allTags
        if tag[0] == "$"
    ]
    tagChanges = [
        tag for tag in allTags
        if tag[0] != '$'
    ]

    if len(selectors) == 0 and not Input.getBool("Confirm: you want to Refactor EVERYTHING??"):
        raise ProgramException("Lmao Oopsie <.<")
    print(f"Refactoring matches to {selectors} with {tagChanges}...")
    for localTags in LocalTags.getAll():
        indices = localTags.getIndicesWith(selectors)
        if len(indices) != 0:
            print(f"Retagging indices {indices}")
            localTags.tagWith(indices, tagChanges).save()
refactorCommand = Command(
    "refactor",
    "Refactor Tags",
    "Find all instances of a set of tags, and add/remove tags from them. Select using $tag and $-tag, then add/remove tags with just tag or -tag like usual. So for example, to replace the tag 'willie' with 'willy', you would call 'refactor $willie -willie willy'.",
    [ Arg.stringType("tags").variable() ],
    refactor,
)

def deunderscore(args):
    addedTags = set([])
    removedTags = set([])
    for localTags in LocalTags.getAll():
        tags = localTags.getAllTags()
        newLocalTags: LocalTags = localTags
        for tag in tags:
            words = tag.split("_")
            if len(words) == 1:
                continue
            Program.printWarning(f"Splitting up {tag}...")
            indices = localTags.getIndicesWith(tag)
            newLocalTags = newLocalTags.withTags(indices, words).withoutTags(indices, [tag])
            addedTags = addedTags.union(set(words))
            removedTags.add(tag)
        newLocalTags.save()
    Program.printSuccess(f" + {list(addedTags)}")
    Program.printError(f" - {list(removedTags)}")
deunderscoreCommand = Command(
    "deunderscore",
    "Remove Underscores",
    "Replace every instance of tags with underscores, with the list of all the underscore-delimited words.",
    [],
    deunderscore,
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

def publish(args):
    File.deleteDirectory("web/data")
    print("Copying from 'exported'...")
    File.copyDirectory("exported", "web/data")
    print("Successfully copied 'exported' into 'web/data' !")
    Program.printSpecial("* You'll still need to manually push those changes!")
publishCommand = Command(
    "publish",
    "Publish Changes",
    "Copies the [exported] folder into [web/data], then copies [web] into [../stardew-png.github.io].",
    [],
    publish,
)

def init():
    print("Initialized.")

Program(
    "Mass Tagger",
    init,
    [
        # tag commands
        listCommand,
        showCommand,
        
        # cleanup commands
        cropCommand,
        cleanCommand,
        deunderscoreCommand,
        refactorCommand,
        
        # export!
        exportCommand,
        progressCommand,
        publishCommand,
    ],
).run()