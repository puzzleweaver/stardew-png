import json
import copy

from utils.file import File
from utils.program_exception import ProgramException
from utils.local_tags import LocalTags

class GlobalTags:
    """A collection of read-only operations on all tags on any sprite."""

    def __init__(self, data):
        self.data = data
    
    def load():
        newData = {}
        allLocalTags = LocalTags.getAll()
        for localTags in allLocalTags:
            for index in localTags.tagsByIndex:
                filename = f"{localTags.directory}/{index}.png"
                newData[filename] = localTags.getTags(index)
        return GlobalTags(newData)

    def getDirectories(self) -> list[str]:
        ret = []
        for key in self.data:
            directory = "/".join(key.split("/")[:-1])
            if directory not in ret:
                ret.append(directory)
        return ret
    
    def getLocalTags(self, directory) -> LocalTags:
        tags = {}
        for filename in File.getNames(directory):
            index = filename.split("/")[-1].split(".")[0]
            if filename in self.data:
                tags[index] = self.data[filename]
        return LocalTags(
            directory,
            tags,
        )

    def fromJson(jsonData):
        return GlobalTags(json.loads(jsonData))
    
    def toJson(self):
        return json.dumps(self.data)
    
    def getFileTags(self, filename):
        try:
            return self.data[filename]
        except:
            return []
    
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
    