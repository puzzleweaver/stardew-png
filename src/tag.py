# Import module
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

for directory in dirs:

    # start with everything in the directory selected. much easier
    selected = File.getNames(directory)
    def display():
        File.displayDirectory(directory, getManifest(), selected)
        print(f"Showing: {directory}")

    display()

    done = False
    while not done:
        manifest = getManifest()

        command = input(" ~> ")
        words = command.split(" ")
        choice = words[0]

        if choice == "s":
            args = words[1:]

            if "*" in args:
                selected = File.getNames(directory)
            else:
                selected.extend([
                    f"{directory}/{arg}.png" for arg in args
                ])

            display()
        elif choice == "rm":
            args = [
                f"{directory}/{word}.png" for word in words[1:]
            ]

            for arg in args:
                confirmation = input(f"Delete {arg}? (Y to confirm)")
                if(confirmation == "Y"):
                    File.deleteFile(arg)
                    display()
                else:
                    print(f"Skipping {arg}.")
        elif choice == "d":
            args = words[1:]

            if "*" in args:
                selected = []
            else:
                excludedFilenames = [
                    f"{directory}/{arg}.png" for arg in args
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
        elif choice == "done":
            # TODO save all the new tags.
            done = True
        elif choice == "skip":
            done = True
        else:
            print(
                "\n".join([
                    "Enter one of the following commands:",
                    "+---------------+",
                    "| s $index ...  | select one or more images, * for all",
                    "|               |",
                    "| d $index ...  | deselect one or more images, * for all",
                    "|               |",
                    "| t $tag ...    | adds tags to all selected",
                    "|               |",
                    # "| ut $tag ...   | removes tags from all selected"
                    # "|               |",
                    "| rm $index ... | deletes specified files",
                    "|               |",
                    "| done          | moves to next set of images",
                    "+---------------+",
                ])
            )
