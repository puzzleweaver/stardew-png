import copy
from typing import Literal

import PIL
from utils.box import Box, Side
from utils.graphics import Graphics
from utils.file import File

class Sheet:
    """Handles a list of subsprites, and operations on that list"""

    filename: str
    boxes: dict[int, Box]

    def __init__(self, filename: str, boxes: dict[int, Box]):
        self.boxes = boxes
        self.filename = filename

    def fromData(data):
        boxes = {}
        for boxData in data["boxes"]:
            boxes[boxData["i"]] = Box.fromData(boxData)
        return Sheet(
            data["filename"],
            boxes,
        )
    
    def toData(self):
        return {
            "filename": self.filename,
            "boxes": [ self.boxes[i].toData(i) for i in self.boxes]
        }

    def initial(filename: str):
        image = File.getImage(filename)
        imgWidth = image.width
        imgHeight = image.height
        return Sheet(
            filename,
            { 0: Box(0, 0, imgWidth, imgHeight) },
        )
    
    def withoutBox(self, index: int):
        newBoxes = copy.deepcopy(self.boxes)
        del newBoxes[index]
        return Sheet(self.filename, newBoxes)
    
    def withoutBoxes(self, indices: list[int]):
        newBoxes = copy.deepcopy(self.boxes)
        for index in indices:
            del newBoxes[index]
        return Sheet(self.filename, newBoxes)
    
    def withBox(self, addedBox: Box):
        newBoxes = copy.deepcopy(self.boxes)
        index = 0
        while index in self.boxes:
            index += 1
        newBoxes[index] = addedBox
        return Sheet(self.filename, newBoxes)

    def withBoxes(self, addedBoxes: list[Box]):
        ret = self
        for addedBox in addedBoxes:
            ret = ret.withBox(addedBox)
        return ret

    def merge(self, index1: int, index2: int):
        box1 = self.boxes[index1]
        box2 = self.boxes[index2]
        newBox = box1.getBoundsOnce(box2)
        indicesToRemove = [
            index for index in self.boxes.keys()
            if self.boxes[index].intersects(newBox)
        ]
        return self.withoutBoxes(indicesToRemove).withBox(newBox)
    
    def getSliced(self, index: int, wide: int, tall: int):
        ret = self
        ret = ret.withoutBox(index)
        ret = ret.withBoxes(self.boxes[index].getSliced(wide, tall))
        return ret
    
    def getCut(self, index: int, side: Side, pixels: int):
        ret = self
        ret = ret.withoutBox(index)
        ret = ret.withBoxes(self.boxes[index].getCut(side, pixels))
        return ret
    
    def getShifted(self, index: int, side: Side, pixels: int):
        newBoxes = copy.deepcopy(self.boxes)

        # update the one actually being shifted...
        newBox = self.boxes[index].getShifted(side, pixels)
        newBoxes[index] = newBox

        # Then try to correct intersections...
        for otherIndex in newBoxes:
            if index == otherIndex: continue
            box = newBoxes[otherIndex]
            if box.intersects(newBox):
                newValue = newBox.getSide(side)
                newBoxes[otherIndex] = box.withSide(Box.opposite(side), newValue)

        # Done!
        return Sheet(self.filename, newBoxes)
    
    def getSubimage(self, index: int):
        image = File.getImage(self.filename)
        subsprite = self.boxes[index]
        return image.crop(
            (
                subsprite.left,
                subsprite.top,
                subsprite.right,
                subsprite.bottom,
            ),
        )
    
    def getDirectory(self):
        return File.getOutputDirectory(self.filename)
    
    def getSubpath(self, index: int):
        dirs = self.filename.split("/")[1:]
        path = f"output/{"/".join(dirs[:-1])}"

        filename = dirs[-1]
        filenameWords = filename.split(".")
        name = filenameWords[0].replace(" ", "_")

        subfilename = ".".join(
            filenameWords[1:-1] +
            [ f"{index}" ] +
            [ filenameWords[-1] ]
        )

        return f"{path}/{name}/{subfilename}"
    
    def getBounds(self, indices: list[int]):
        boxes = [
            self.boxes[index]
            for index in indices
        ]
        return Box.getBounds(boxes)
        
    def drawOn(self, image: PIL.Image, viewport: Box):
        image = Graphics.withBackground(image)
        factor = 6
        size = max(viewport.width, viewport.height)
        disp = Graphics.scale(image, factor, size)
        for index in self.boxes:
            box = self.boxes[index]
            box.scale(factor).drawOn(disp, f"{index}")
        File.displayImage(disp.crop(viewport.scale(factor).getLTRB()))

    def saveFinalImages(self):
        for index in self.boxes:
            subimage = Graphics.crop(self.getSubimage(index))
            subfilename = self.getSubpath(index)

            if subimage is None:
                print(f"Skipping {subfilename} bc its empty")
                continue

            print(f"Saving {subfilename}.")
            File.saveImage(subfilename, subimage)
