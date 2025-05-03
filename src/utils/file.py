
import json
import os
import subprocess

from PIL import Image

from utils.graphics import Graphics

class File:
    """Handles all file IO operations."""
    height = 15

    def setImageHeight(newHeight):
        File.height = newHeight

    def hasExtension(filename, extension):
        """Checks whether a filename has a specified extension."""
        extensionLength = len(extension)
        if(len(filename) < extensionLength): return False
        return filename[-extensionLength-1:] == f".{extension}"
    
    def exists(filename):
        return os.path.isfile(filename)

    def createDirectory(path):
        print(f"Trying to create dir {path}")
        subprocess.Popen(f'mkdir -p {path}', shell=True).wait()

    def deleteFile(filename):
        subprocess.Popen(f'rm {filename}', shell=True).wait()

    def getNames(directory):
        """
        Returns relative names of all files under the given directory,
        passing the condition passed in.
        
        Parameters
        ----------
        directory: str
            Path of the directory to start from.
        extension: str, optional
            Only files with this string as a suffix are returned.
            If extension None is passed in, all file names will be returned.
        """
        ret = []
        for path, folders, files in os.walk(directory):
            for filename in files:
                ret.append(f"{path}/{filename}")
            for folder_name in folders:
                ret.extend(File.getNames(f"{path}/{folder_name}"))
            break
        return [
            filename for filename in ret
            if File.hasExtension(filename, "png")
        ]
    
    def getDirectories(directory):
        allNames = File.getNames(directory)
        ret = []
        for name in allNames:
            words = name.split("/")
            newDir = "/".join(words[:-1])
            if not newDir in ret:
                ret.append(newDir)
        return ret

    def getImage(filename):
        return Image.open(filename)

    def saveImage(filename, image):
        print(f"saving image {filename}...")

        # create the directory if it doesn't exist :eyeroll:
        path = '/'.join(filename.split('/')[:-1])
        File.createDirectory(path)

        image.save(filename)
        print("done.")

    def displayImageFile(filename):
        """Displays an image by filename. """
        subprocess.Popen('clear', shell=True).wait()
        subprocess.Popen(f'imgcat --height {File.height} "{filename}"', shell=True).wait()

    def displayImage(image):
        """Displays an image by saving it as a temporary file and then using displayImageFile."""
        filename = "temp/temp0.png"
        image.save(filename, "PNG")
        File.displayImageFile(filename)

    def getIndex(filename):
        return filename.split("/")[-1].replace(".png", "").replace(".json", "")

    def readText(filename, fallback):
        try:
            file = open(filename, 'r')
            return file.read()
        except:
            return fallback
        
    def writeText(filename, contents):
        file = open(filename, "w")
        file.write(contents)

    def displayDirectory(directory, manifest, selected):
        filenames = File.getNames(directory)
        File.displayImage(
            Graphics.collect(
                filenames,
                [ File.getImage(filename) for filename in filenames ],
                manifest,
                selected,
            )
        )