# Import module
from math import ceil
import sys
from utils.file import File
from utils.manifest import Manifest

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
    global currentPageIndex
    currentPageIndex = currentPageIndex + count
    if currentPageIndex < 0:
        currentPageIndex = 0
    if currentPageIndex >= len(pages):
        currentPageIndex = len(pages)-1

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

recalculate()

while True:
    currentPage = pages[currentPageIndex]

    def filenameByIndex(index):
        global currentPage
        matches = [
            filename for filename in currentPage
            if f"/{index}.png" in filename
        ]
        if len(matches) == 0: raise f"Fatal: No file at index!! {index} on {currentPage}"
        if len(matches) > 1: raise f"Fatal: Too many files at index!! {matches}"
        return matches[0]

    def display():
        global currentPageIndex
        File.displayDirectory(currentPage, getManifest(), selected)
        directory = "/".join(currentPage[0].split("/")[:-1])
        print(f"Current: {currentPageIndex+1}/{len(pages)}, {directory}")

    # start with everything in the directory selected. much easier
    selected = currentPage

    display()

    while True:
        manifest = getManifest()

        command = input(" ~> ")
        words = command.split(" ")
        choice = words[0]

        if choice == "s":
            args = words[1:]

            if "*" in args:
                selected = currentPage
            else:
                selected.extend([
                    file for file in [
                        filenameByIndex(arg) for arg in args
                    ]
                    if file in currentPage
                ])

            display()
        elif choice == "rm":
            args = words[1:]

            anyDeleted = False
            for arg in args:
                filename = filenameByIndex(arg)
                File.displayImageFile(filename)
                confirmation = input(f"Delete {filename}? (Y to confirm)")
                if(confirmation == "Y"):
                    File.deleteFile(filename)
                    anyDeleted = True
                else:
                    print(f"Skipping {filename}.")
            if anyDeleted:
                recalculate()
                break
        elif choice == "d":
            args = words[1:]

            if "*" in args:
                selected = []
            else:
                excludedFilenames = [
                    filenameByIndex(arg) for arg in args
                ]
                selected = [
                    filename for filename in selected
                    if filename not in excludedFilenames
                ]

            display()
        elif choice == "t":
            if len(selected) == 0:
                print("Nothing selected.")
                continue

            newTags = words[1:]
            newManifest = manifest.withTagsAdded(selected, newTags)
            File.writeText("output/manifest.json", newManifest.toJson())
            display()
        elif choice == "ut":
            if len(selected) == 0:
                print("Nothing selected.")
                continue

            newTags = words[1:]
            newManifest = manifest.withTagsRemoved(selected, newTags)
            File.writeText("output/manifest.json", newManifest.toJson())
            display()
        elif choice == "c":
            if currentPageIndex == len(pages)-1:
                print("Already at end.")
                continue

            count = 1
            if len(words) == 2:
                try:
                    count = int(words[1])
                except:
                    print("Count must be an integer.")
                    continue
            # TODO navigate to a different page.
            step(count)
            break
        elif choice == "p":
            if currentPageIndex == 0:
                print("Already at beginning.")
                continue

            count = 1
            if len(words) == 2:
                try:
                    count = int(words[1])
                except:
                    print("Count must be an integer.")
                    continue
            # TODO navigate to a different page.
            step(-count)
            break
        elif choice == "exit":
            print("Bye Bye ^_^")
            exit()
        else:
            print(
                "\n".join([
                    "Enter one of the following commands:",
                    "+---------------+",
                    "| s $index ...  | select one or more images, * for all",
                    "|               |",
                    "| d $index ...  | deselect one or more images, * for all",
                    "|               |",
                    "| t $tag ...    | adds specified tags to all selected",
                    "|               |",
                    "| ut $tag ...   | removes specified tags from all selected",
                    "|               |",
                    "| rm $index ... | deletes specified files",
                    "|               |",
                    "| c $count?     | navigates/continues forward 1 or more pages",
                    "|               |",
                    "| p $count?     | navigates/continues backwards 1 or more pages",
                    "|               |",
                    "| e             | exit program.",
                    "+---------------+",
                ])
            )