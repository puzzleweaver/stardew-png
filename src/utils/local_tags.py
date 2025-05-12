
import copy
from utils.file import File


class LocalTags:
    directory: str
    tagsByIndex: dict[str, list[str]]

    def __init__(self, directory, tagsByIndex) -> 'LocalTags':
        self.directory = directory
        self.tagsByIndex = tagsByIndex

    def getIndices(self) -> list[str]:
        return self.tagsByIndex.keys()

    def getAll() -> list['LocalTags']:
        directories = File.getDirectories("output")
        ret = []
        for directory in directories:
            ret.append(
                LocalTags.load(directory)
            )
        return ret

    def initial(directory: str) -> 'LocalTags':
        return LocalTags(directory, {})
    
    def getFilename(directory: str) -> str:
        return f"{directory}/tags.json"
    
    def load(directory: str) -> 'LocalTags':
        filename = LocalTags.getFilename(directory)
        return LocalTags(directory, File.readJson(filename, {}))
        
    def save(self) -> None:
        filename = LocalTags.getFilename(self.directory)
        File.writeJson(filename, self.tagsByIndex)

    def withTag(self, index: str, tag: str) -> 'LocalTags':
        index = str(index)
        newTagsByIndex = copy.deepcopy(self.tagsByIndex)

        if not index in newTagsByIndex: newTagsByIndex[index] = []
        if tag in newTagsByIndex[index]: return self
        newTagsByIndex[index].append(tag)

        return LocalTags(self.directory, newTagsByIndex)

    def withoutTag(self, index: int, tag: str) -> 'LocalTags':
        index = str(index)
        newTagsByIndex = copy.deepcopy(self.tagsByIndex)

        if not index in newTagsByIndex: return self
        if not tag in newTagsByIndex[index]: return self
        newTagsByIndex[index].remove(tag)

        return LocalTags(self.directory, newTagsByIndex)
    
    def withoutIndex(self, index: str) -> 'LocalTags':
        index = str(index)
        if not index in self.tagsByIndex: return self
        
        newTagsByIndex = copy.deepcopy(self.tagsByIndex)
        del newTagsByIndex[str(index)]
        return LocalTags(self.directory, newTagsByIndex)

    def withTags(self, indices: list[str], tags: list[str]) -> 'LocalTags':
        ret = self
        for index in indices:
            for tag in tags:
                ret = ret.withTag(index, tag)
        return ret
    
    def tagWith(self, indices: list[int], tags: list[str]) -> 'LocalTags':
        tagsToAdd = [
            tag for tag in tags
            if tag[0] != '-'
        ]
        tagsToRemove = [
            tag[1:] for tag in tags
            if tag[0] == '-'
        ]
        return self.withTags(indices, tagsToAdd).withoutTags(indices, tagsToRemove)

    def getTags(self, index: str) -> list[str]:
        index = str(index)
        return self.tagsByIndex.get(index, [])

    def withoutTags(self, indices: list[str], tags: list[str]) -> 'LocalTags':
        ret = self
        for index in indices:
            for tag in tags:
                ret = ret.withoutTag(index, tag)
        return ret

    def toString(self) -> str:
        return f"{self.directory}: {self.tagsByIndex}"
    