
from textwrap import wrap
import json
import copy

from utils.file import File

class Manifest:

    def __init__(self, data):
        self.data = data

    def load():
        return Manifest.fromJson(
            File.readText("output/manifest.json", "{}")
        )

    def save(self):
        print("Saving manifest...")
        File.writeText("output/manifest.json", self.toJson())

    def fromJson(jsonData):
        return Manifest(json.loads(jsonData))
    
    def toJson(self):
        return json.dumps(self.data)
    
    def getFileTags(self, filename):
        try:
            return self.data[filename]
        except:
            return []
    
    def withTags(self, filenames, addedTags):
        newData = copy.deepcopy(self.data)
        for filename in filenames:
            newTags = self.getFileTags(filename)
            for addedTag in addedTags:
                if not addedTag in newTags:
                    newTags.append(addedTag)
            newData[filename] = newTags
        return Manifest(newData)
    
    def withoutTags(self, filenames, removedTags):
        newData = copy.deepcopy(self.data)
        for filename in filenames:
            newTags = [
                tag for tag in self.getFileTags(filename)
                if not tag in removedTags
            ]
            newData[filename] = newTags
        return Manifest(newData)

    def getAllTags(self):
        filenames = list(self.data.keys())
        tags = []
        for filename in filenames:
            fileTags = self.getFileTags(filename)
            for tag in fileTags:
                if tag not in tags:
                    tags.append(tag)
        return tags
    
    def getSharedTags(self, tag):
        filesWithTag = self.getFilesWithTag(tag)
        ret = []
        for file in filesWithTag:
            others = self.getFileTags(file)
            for other in others:
                if other not in ret:
                    ret.append(other)
        return ret
    
    def getFilesWithTag(self, tag):
        filenames = list(self.data.keys())
        ret = []
        for filename in filenames:
            if tag in self.getFileTags(filename):
                ret.append(filename)
        return ret
    
    def getFilesWithTags(self, tags):
        filenames = list(self.data.keys())
        ret = []
        for filename in filenames:
            good = True
            for tag in tags:
                if tag not in self.getFileTags(filename):
                    good = False
                    break
            if good:
                ret.append(filename)
        return ret
    
    def clean(self):
        """
        Removes:
         - all references to files that don't exist
         - the empty tag
        """
        filenames = list(self.data.keys())
        removedFiles = []
        newData = copy.deepcopy(self.data)
        for filename in filenames:
            if not File.exists(filename):
                del newData[filename]
                removedFiles.append(filename)
        

        return (Manifest(newData), removedFiles)
    
    def withoutTag(self, tag):
        return self.withoutTags(self.getFilesWithTag(tag), [tag])