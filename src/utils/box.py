

from math import ceil
from typing import Literal

from utils.graphics import Graphics

Side = Literal['l', 'r', 't', 'b']

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

    def fromLTRB(l, t, r, b):
        return Box(l, t, r - l, b - t)

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
    
    def getSliced(self, numX: int, numY: int):
        newBoxes = []
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
                newBoxes.append(
                    Box(
                        self.left + xValues[i],
                        self.top + yValues[j],
                        xValues[i+1] - xValues[i],
                        yValues[j+1] - yValues[j],
                    )
                )
        return newBoxes
    
    def getCut(self, side: Side, pixels):
        if side == 'l':
            return [ self.withSide('r', self.left+pixels), self.withSide('l', self.left+pixels) ]
        if side == 't':
            return [ self.withSide('b', self.top+pixels), self.withSide('t', self.top+pixels) ]
        if side == 'r':
            return [ self.withSide('r', self.right+pixels), self.withSide('l', self.right+pixels) ]
        if side == 'b':
            return [ self.withSide('b', self.bottom+pixels), self.withSide('t', self.bottom+pixels) ]
        else: raise f"Invalid Side: {side}"

    def getShifted(self, side: Side, pixels: int):
        if side == 'l': return self.withSide('l', self.left + pixels)
        if side == 't': return self.withSide('t', self.top + pixels)
        if side == 'r': return self.withSide('r', self.right + pixels)
        if side == 'b': return self.withSide('b', self.bottom + pixels)

    def withSide(self, side: Side, newValue: int):
        if side == 'l': return Box.fromLTRB(newValue, self.top, self.right, self.bottom)
        if side == 't': return Box.fromLTRB(self.left, newValue, self.right, self.bottom)
        if side == 'r': return Box.fromLTRB(self.left, self.top, newValue, self.bottom)
        if side == 'b': return Box.fromLTRB(self.left, self.top, self.right, newValue)
        raise ValueError("Side must be l/t/r/b.")
    
    def getSide(self, side: Side):
        if side == 'l': return self.left
        if side == 't': return self.top
        if side == 'r': return self.right
        if side == 'b': return self.bottom

    def opposite(side: Side):
        if side == 'r': return 'l'
        if side == 'b': return 't'
        if side == 'l': return 'r'
        if side == 't': return 'b'

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
