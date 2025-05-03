
from textwrap import wrap
import json
import copy

class Manifest:

    def __init__(self, data):
        self.data = data

    def fromJson(jsonData):
        return Manifest(json.loads(jsonData))
    
    def toJson(self):
        return json.dumps(self.data)
    
    def getFileTags(self, filename):
        try:
            return self.data[filename]
        except:
            return []
    
    def getFileTagString(self, filename):
        tags = self.getFileTags(filename)
        return "\n".join(
            wrap(
                " ".join(tags),
                13,
            )
        ).replace(" ", ",")
    
    def withTagsAdded(self, filenames, addedTags):
        newData = copy.deepcopy(self.data)
        for filename in filenames:
            newTags = self.getFileTags(filename)
            for addedTag in addedTags:
                if not addedTag in newTags:
                    newTags.append(addedTag)
            newData[filename] = newTags
        return Manifest(newData)
    
    def withTagsRemoved(self, filenames, removedTags):
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