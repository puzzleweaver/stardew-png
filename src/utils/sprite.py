import copy
from math import ceil
import random
from utils.graphics import Graphics
from utils.file import File
from PIL import Image

class Box:
    """
    This class describes all the data to be collected about an image,
    for example the sprites it contains plus metadata about those sprites.
    """

    left: int
    top: int
    right: int
    bottom: int
    width: int
    height: int

    def __init__(self, left, top, width, height):
        left = int(left)
        top = int(top)
        width = int(width)
        height = int(height)

        if(width <= 0): raise ValueError("Box width must be >0")
        if(height <= 0): raise ValueError("Box height must be >0")
        # if(left < 0): raise ValueError("Box left must be >= 0")
        # if(top < 0): raise ValueError("Box top must be >= 0")

        self.left = left
        self.top = top
        self.width = width
        self.height = height
        self.right = left + width
        self.bottom = top + height

    def getBounds(boxes):
        if len(boxes) == 0:
            raise ValueError("Must include at least one box.")
        ret = boxes[0]
        for box in boxes:
            ret = ret.getBoundsOnce(box)
        return ret
    
    def getBoundsOnce(self, other):
        left = min(self.left, other.left)
        top = min(self.top, other.top)
        right = max(self.right, other.right)
        bottom = max(self.bottom, other.bottom)
        return Box(
            left,
            top,
            right - left,
            bottom - top,
        )
    
    def divisorsOf(n):
        ret = []
        for i in range(2, ceil(n/8)):
            if n % i == 0:
                ret.append(i)
        return ret

    def getDivisors(self):
        return (
            Box.divisorsOf(self.width),
            Box.divisorsOf(self.height),
        );

    def getLTRB(self):
        return (
            self.left,
            self.top,
            self.right,
            self.bottom,
        )
    
    def zoom(self, amount):
        return Box(
            self.left + self.width*amount,
            self.top + self.height*amount,
            self.width*(1 - 2*amount),
            self.height*(1 - 2*amount),
        )
    
    def intersects(self, other):
        l,t,r,b = self.getLTRB()
        ol,ot,oR,ob = other.getLTRB()
        maxSeparation = max(
            max(
                ol - r,
                l - oR,
            ),
            max(
                ot - b,
                t - ob,
            ),
        )
        return maxSeparation < 0
    
    def contains(self, x, y):
        return x >= self.left and x < self.right and y >= self.top and y < self.bottom
    
    def scale(self, factor):
        return Box(
            self.left*factor,
            self.top*factor,
            self.width*factor,
            self.height*factor,
        )
    
    def getSliced(self, numX, numY):
        newSubsprites = []
        if(numX  > self.width/2 or numY > self.height/2):
            raise ValueError(f"Cannot divide {self.width}x{self.height} into {numX}x{numY}.")
        
        xValues = [
            int(self.width*i/numX) for i in range(0, numX+1)
        ]
        yValues = [
            int(self.height*i/numY) for i in range(0, numY+1)
        ]
        
        xValues[-1] = self.width
        yValues[-1] = self.height

        for j in range(numY):
            for i in range(numX):
                newSubsprites.append(
                    Box(
                        self.left + xValues[i],
                        self.top + yValues[j],
                        xValues[i+1] - xValues[i],
                        yValues[j+1] - yValues[j],
                    )
                )
        return newSubsprites
    
    def getCut(self, axis, pixels):
        if axis == 'x':
            return [
                Box(self.left, self.top, pixels, self.height),
                Box(self.left+pixels, self.top, self.width-pixels, self.height)
            ]
        elif axis == 'y':
            return [
                Box(self.left, self.top, self.width, pixels),
                Box(self.left, self.top+pixels, self.width, self.height-pixels)
            ]
        else: raise f"Invalid Axis: {axis}"

    def getShifted(self, side, pixels):
        if side == 'l':
            return Box(self.left+pixels, self.top, self.width-pixels, self.height)
        if side == 't':
            return Box(self.left, self.top+pixels, self.width, self.height-pixels)
        if side == 'r':
            return Box(self.left, self.top, self.width+pixels, self.height)
        if side == 'b':
            return Box(self.left, self.top, self.width, self.height+pixels)

    def drawRect(self, image, fill=None, stroke="red"):
        Graphics.drawRect(
            image, 
            self.left, 
            self.top, 
            self.width-1, 
            self.height-1, 
            fill=fill,
            stroke=stroke,
        )

    def drawText(self, image, text, color="black"):
        Graphics.drawText(
            image,
            self.left+self.width/2,
            self.top+self.height/2,
            self.width/3,
            self.height/3,
            text,
            fill=color,
        )

    def scale(self, factor):
        return Box(
            self.left * factor,
            self.top * factor,
            self.width * factor,
            self.height * factor,
        )

    def drawOn(self, image, text):
        self.drawRect(image)
        self.drawText(image, text)

class Sheet:
    """Handles a list of subsprites, and operations on that list"""

    filename: str
    subsprites: list[Box]

    def __init__(self, filename, subsprites):
        self.subsprites = subsprites
        self.filename = filename

    def initial(filename):
        image = File.getImage(filename)
        imgWidth = image.width
        imgHeight = image.height
        return Sheet(
            filename,
            [ Box(0, 0, imgWidth, imgHeight) ]
        )

    def merge(self, index1, index2):
        box1 = self.subsprites[index1]
        box2 = self.subsprites[index2]
        newSubsprite = box1.getBoundsOnce(box2)
        return Sheet(
            self.filename,
            [
                subsprite for subsprite in self.subsprites
                if not subsprite.intersects(newSubsprite)
            ] + [ newSubsprite ],
        )
    
    def getSliced(self, index, wide, tall):
        oldSubsprite = self.subsprites[index]
        newSubsprites = oldSubsprite.getSliced(wide, tall)
        return Sheet(
            self.filename,
            [
                subsprite for subsprite in self.subsprites
                if subsprite != oldSubsprite
            ] + newSubsprites
        )
    
    def getCut(self, index, axis, pixels):
        oldSubsprite = self.subsprites[index]
        newSubsprites = oldSubsprite.getCut(axis, pixels)
        return Sheet(
            self.filename,
            [
                subsprite for subsprite in self.subsprites
                if subsprite != oldSubsprite
            ] + newSubsprites
        )
    
    def getShifted(self, index, side, pixels):
        newSubsprites = copy.deepcopy(self.subsprites)
        newSubsprites[index] = self.subsprites[index].getShifted(side, pixels)
        return Sheet(self.filename, newSubsprites)
    
    def getSubimage(self, index):
        image = File.getImage(self.filename)
        subsprite = self.subsprites[index]
        return image.crop(
            (
                subsprite.left, 
                subsprite.top, 
                subsprite.right, 
                subsprite.bottom,
            ),
        )
    
    def getSubpath(self, index):
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
    
    def getBounds(self, indices):
        boxes = [
            self.subsprites[index]
            for index in indices
        ]
        print("Got here...")
        return Box.getBounds(boxes)
        
    def drawOn(self, image, viewport):
        image = Graphics.withBackground(image)
        factor = 6
        size = max(viewport.width, viewport.height)
        disp = Graphics.scale(image, factor, size)
        index = 0
        for box in self.subsprites:
            box.scale(factor).drawOn(disp, f"{index}")
            index += 1
        print(viewport.scale(factor).getLTRB())
        File.displayImage(disp.crop(viewport.scale(factor).getLTRB()))

    def save(self):
        for i in range(len(self.subsprites)):
            subimage = self.getSubimage(i)
            subfilename = self.getSubpath(i)
            print(subfilename)
            File.saveImage(subfilename, subimage)
            # File.saveMetadataJson()