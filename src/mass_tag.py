# Import module
from string import ascii_lowercase

from termcolor import colored
from utils.file import File
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
        Manifest.load(),
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
    saveManifest(newManifest)
rmtagCommand = Command(
    "del", "Delete Tag",
    "Delete a tag from the entire manifest.",
    [ Arg.stringType("tag") ],
    rmtag
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
    tags
)

Program(
    "Mass Tagger",
    recalculate,
    [ 
        rmtagCommand,
        tagsCommand, 
        whichCommand,
        cleanCommand,
    ],
).run()