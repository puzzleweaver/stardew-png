
import copy
from utils.file import File


class LocalTags:
    directory: str
    tagsByIndex: dict[int, list[str]]

    def __init__(self, directory, tagsByIndex) -> 'LocalTags':
        self.directory = directory
        self.tagsByIndex = tagsByIndex

    def getAll() -> list['LocalTags']:
        directories = File.getDirectories("output")
        ret = []
        for directory in directories:
            ret.append(
                LocalTags.load(directory)
            )
        return ret

    def initial(directory) -> 'LocalTags':
        return LocalTags(directory, {})
    
    def getFilename(directory) -> str:
        return f"{directory}/tags.json"
    
    def load(directory) -> 'LocalTags':
        filename = LocalTags.getFilename(directory)
        return LocalTags(directory, File.readJson(filename, {}))
        
    def save(self) -> None:
        filename = LocalTags.getFilename(self.directory)
        File.writeJson(filename, self.tagsByIndex)

    def withTag(self, index, tag) -> 'LocalTags':
        index = str(index)
        newTagsByIndex = copy.deepcopy(self.tagsByIndex)

        if not index in newTagsByIndex: newTagsByIndex[index] = []
        if tag in newTagsByIndex[index]: return self
        newTagsByIndex[index].append(tag)

        return LocalTags(self.directory, newTagsByIndex)

    def withoutTag(self, index, tag) -> 'LocalTags':
        index = str(index)
        newTagsByIndex = copy.deepcopy(self.tagsByIndex)

        if not index in newTagsByIndex: return self
        if not tag in newTagsByIndex[index]: return self
        newTagsByIndex[index].remove(tag)

        return LocalTags(self.directory, newTagsByIndex)
    
    def withoutIndex(self, index) -> 'LocalTags':
        if not index in self.tagsByIndex: return self
        
        newTagsByIndex = copy.deepcopy(self.tagsByIndex)
        del newTagsByIndex[str(index)]
        return LocalTags(self.directory, newTagsByIndex)

    def withTags(self, indices, tags) -> 'LocalTags':
        ret = self
        for index in indices:
            for tag in tags:
                ret = ret.withTag(index, tag)
        return ret

    def getTags(self, index) -> list[str]:
        index = str(index)
        return self.tagsByIndex.get(index, [])

    def withoutTags(self, indices, tags) -> 'LocalTags':
        ret = self
        for index in indices:
            for tag in tags:
                ret = ret.withoutTag(index, tag)
        return ret

    def toString(self) -> str:
        return f"{self.directory}: {self.tagsByIndex}"
    