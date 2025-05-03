from utils.graphics import Graphics
from utils.file import File
from PIL import Image

class Subsprite:
    """
    This class describes all the data to be collected about an image,
    for example the sprites it contains plus metadata about those sprites.
    """

    left: int
    top: int
    width: int
    height: int

    def __init__(self, left, top, width, height):
        self.left = int(left)
        self.top = int(top)
        self.width = int(width)
        self.height = int(height)

    def getRight(self):
        return self.left + self.width
    
    def getBottom(self):
        return self.top + self.height

    def getLeftTop(self):
        return (self.left, self.top)
    
    def getRightBottom(self):
        return (
            self.getRight(),
            self.getBottom(),
        )
    
    def intersects(self, other):
        (l, t) = self.getLeftTop()
        (r, b) = self.getRightBottom()
        (ol, ot) = other.getLeftTop()
        (oR, ob) = other.getRightBottom()
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
    
    def scale(self, factor):
        return Subsprite(
            self.left*factor,
            self.top*factor,
            self.width*factor,
            self.height*factor,
        )
    
    def getSliced(self, wide, tall):
        spriteWidth = self.width/wide
        spriteHeight = self.height/tall
        newSubsprites = []
        for i in range(wide):
            for j in range(tall):
                newSubsprites.append(
                    Subsprite(
                        self.left + i*spriteWidth, 
                        self.top + j*spriteHeight, 
                        spriteWidth,
                        spriteHeight,   
                    )
                )
        return newSubsprites
    
    def getCut(self, axis, pixels):
        if axis == 'x':
            return [
                Subsprite(self.left, self.top, pixels, self.height),
                Subsprite(self.left+pixels, self.top, self.width-pixels, self.height)
            ]
        elif axis == 'y':
            return [
                Subsprite(self.left, self.top, self.width, pixels),
                Subsprite(self.left, self.top+pixels, self.width, self.height-pixels)
            ]
        else: raise f"Invalid Axis: {axis}"

    def drawOn(self, image, text):
        Graphics.drawRect(image, self.left, self.top, self.width, self.height)
        Graphics.drawText(
            image,
            self.left+self.width/2,
            self.top+self.height/2,
            text,
            min(self.width, self.height)/3,
        )

class Sheet:
    """Handles a list of subsprites, and operations on that list"""

    filename: str
    subsprites: list[Subsprite]

    def __init__(self, filename, subsprites):
        self.subsprites = subsprites
        self.filename = filename

    def initial(filename):
        image = File.getImage(filename)
        imgWidth = image.width
        imgHeight = image.height
        return Sheet(
            filename,
            [Subsprite(0, 0, imgWidth, imgHeight)]
        )
    
    def merge(self, topleftIndex, bottomrightIndex):
        (left, top) = self.subsprites[topleftIndex].getLeftTop()
        (right, bottom) = self.subsprites[bottomrightIndex].getRightBottom()

        if left > right or top > bottom:
            print("Invalid merge, skipping.")
            return self
        
        newSubsprite = Subsprite(left, top, right-left, bottom-top)
        return Sheet(
            self.filename, 
            [
                subsprite for subsprite in self.subsprites
                if subsprite.intersects(newSubsprite) == False
            ] + [ newSubsprite ],
        )
    
    def slice(self, index, wide, tall):
        oldSubsprite = self.subsprites[index]
        newSubsprites = oldSubsprite.getSliced(wide, tall)
        return Sheet(
            self.filename,
            [
                subsprite for subsprite in self.subsprites
                if subsprite != oldSubsprite
            ] + newSubsprites
        )
    
    def cut(self, index, axis, pixels):
        oldSubsprite = self.subsprites[index]
        newSubsprites = oldSubsprite.getCut(axis, pixels)
        return Sheet(
            self.filename,
            [
                subsprite for subsprite in self.subsprites
                if subsprite != oldSubsprite
            ] + newSubsprites
        )
    
    def getSubimage(self, index):
        image = File.getImage(self.filename)
        subsprite = self.subsprites[index]
        return image.crop(
            (
                subsprite.left, 
                subsprite.top, 
                subsprite.getRight(), 
                subsprite.getBottom(),
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
        
    def drawOn(self, image):
        factor = 6
        disp = Graphics.scale(image, factor)
        index = 0
        for sprite in self.subsprites:
            sprite.scale(factor).drawOn(disp, f"{index}")
            index += 1
        File.displayImage(disp)

    def save(self):
        for i in range(len(self.subsprites)):
            subimage = self.getSubimage(i)
            subfilename = self.getSubpath(i)
            print(subfilename)
            File.saveImage(subfilename, subimage)
            # File.saveMetadataJson()