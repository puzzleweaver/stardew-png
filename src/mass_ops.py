# Import module
import json
from string import ascii_lowercase
import traceback

from termcolor import colored
from utils.file import File
from utils.graphics import Graphics
from utils.manifest import Manifest
from utils.program import Arg, Command, Program

File.setImageHeight(40)

def recalculate():
    global manifest
    manifest = Manifest.load()

# Which
def which(args):
    tags = args["tags"]

    filesWithTag = manifest.getFilesWithTags(tags)
    filesWithTag.sort()
    
    File.displayList(
        filesWithTag,
        [" ".join(manifest.getFileTags(file)) for file in filesWithTag],
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
    tag = args["tag"]
    newManifest = manifest.withoutTag(tag)
    newManifest.save()
rmtagCommand = Command(
    "rmtag", "Remove Tag",
    "Remove a tag everywhere it appears.",
    [ Arg.stringType("tag") ],
    rmtag
)

def distributeManifest(args):
    manifest = Manifest.load()
    directories = manifest.getDirectories()
    for directory in directories:
        try:
            tagManifest = manifest.getSubmanifest(directory)
            tagManifest.save()
        except Exception as e:
            print(e)
            traceback.print_exc()
distributeCommand = Command(
    "distribute",
    "Redistribute Manifest",
    "Take the singular manifest.json file and save it as individual tags.json files in each image's directory.",
    [],
    distributeManifest,
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

# Clean Manifest
def clean(args):
    newManifest, removed = Manifest.load().clean()
    newManifest.save()
    print(f"Removed tags from manifest: {' '.join(removed)}")
cleanCommand = Command(
    "clean", "Clean Manifest",
    "Removes all nonexistant files from the manifest.",
    [],
    clean,
)

# List Tags
def tags(args):
    manifest = Manifest.load()
    allTags = manifest.getAllTags()
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
                f"{tag}({len(manifest.getFilesWithTag(tag))})"
                for tag in tagsWithC
            ]),
            col,
        )
        toggle = not toggle
        print(colored(f"{c.upper()}: {tagsString}", col))
tagsCommand = Command(
    "list", "List Tags",
    "List all tags.",
    [],
    tags,
)

def exportFunction(args):
    Program.printSpecial("Exporting...")
    
    # delete existing exported/ directory
    File.deleteDirectory("exported")

    # make sure the folders involved are created...
    File.ensureFolderExists("exported/sprites/")
    File.ensureFolderExists("exported/tags/")
    
    # create exported/sprites/ directory and copy the entire output/ folder into it
    File.copyDirectory("output/", "exported/sprites/")
    File.deleteFile("exported/sprites/manifest.json", confirm=False)

    # create files:
    manifest: Manifest = Manifest.load()

    #  exported/all_tags.json: lists all tags on any image.
    allTags = manifest.getAllTags()
    File.writeJson("exported/all_tags.json", allTags)

    # helper function for transforming the manifest's filenames so that things work right
    def correct(filename: str):
        return "/".join(filename.split("/")[1:])

    #  exported/tags/<tag>.json: lists all files associated with the tag.
    for tag in allTags:
        filesWithTag = manifest.getFilesWithTag(tag)
        filesWithTag = [
            correct(filename) for filename in filesWithTag
        ]
        sharedTags = manifest.getSharedTags(tag)
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
        fileTags = manifest.getFileTags(f"output/{file}")
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
        tagsCommand, 
        whichCommand,
        
        # cleanup commands
        cleanCommand,
        cropCommand,
        
        # export!
        exportCommand,
    ],
).run()