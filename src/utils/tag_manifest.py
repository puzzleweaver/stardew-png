
from utils.file import File


class TagManifest:

    directory: str
    tagsByIndex: dict[int, list[str]]

    def __init__(self, directory, tagData):
        self.directory = directory
        self.tagsByIndex = tagData

    def initial(directory):
        return TagManifest(directory, {})
        
    def save(self):
        File.writeJson(f"{self.directory}/tags.json", self.tagsByIndex)

    def addTags(self, indices, tags):
        for index in indices:
            for tag in tags:
                if tag not in self.tagsByIndex[index]:
                    self.tagsByIndex[index].append(tag)

    def removeTags(self, indices, tags):
        for index in indices:
            for tag in tags:
                if tag in self.tagsByIndex[index]:
                    self.tagsByIndex[index].remove(tag)

    def toString(self):
        return f"{self.directory}: {self.tagsByIndex}"
    