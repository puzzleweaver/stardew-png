
import copy
from utils.file import File


class Tags:
    directory: str
    tagsByIndex: dict[int, list[str]]

    def __init__(self, directory, tagsByIndex):
        self.directory = directory
        self.tagsByIndex = tagsByIndex

    def initial(directory):
        return Tags(directory, {})
    
    def getFilename(directory):
        return f"{directory}/tags.json"
    
    def load(directory):
        filename = Tags.getFilename(directory)
        return Tags(directory, File.readJson(filename, {}))
        
    def save(self):
        filename = Tags.getFilename(self.directory)
        File.writeJson(filename, self.tagsByIndex)

    def withTag(self, index, tag):
        index = str(index)
        newTagsByIndex = copy.deepcopy(self.tagsByIndex)

        if not index in newTagsByIndex: newTagsByIndex[index] = []
        if tag in newTagsByIndex[index]: return self
        newTagsByIndex[index].append(tag)

        return Tags(self.directory, newTagsByIndex)

    def withoutTag(self, index, tag):
        index = str(index)
        newTagsByIndex = copy.deepcopy(self.tagsByIndex)

        if not index in newTagsByIndex: return self
        if not tag in newTagsByIndex[index]: return self
        newTagsByIndex[index].remove(tag)

        return Tags(self.directory, newTagsByIndex)
    
    def withoutIndex(self, index):
        if not index in self.tagsByIndex: return self
        
        newTagsByIndex = copy.deepcopy(self.tagsByIndex)
        del newTagsByIndex[str(index)]
        return Tags(self.directory, newTagsByIndex)

    def withTags(self, indices, tags):
        ret = self
        for index in indices:
            for tag in tags:
                ret = ret.withTag(index, tag)
        return ret

    def getTags(self, index):
        index = str(index)
        return self.tagsByIndex.get(index, [])

    def withoutTags(self, indices, tags):
        ret = self
        for index in indices:
            for tag in tags:
                ret = ret.withoutTag(index, tag)
        return ret

    def toString(self):
        return f"{self.directory}: {self.tagsByIndex}"
    