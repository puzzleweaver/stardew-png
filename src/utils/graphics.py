
from math import ceil, sqrt
from PIL import Image, ImageDraw, ImageFont
from textwrap import wrap

class Graphics:
    """This class collects all of the image rendering used in the sprite unpacker."""

    def getBackground(width, height):
        image = Image.new('RGBA', (width, height), "#dddddd")
        dim = 5
        if max(width, height) > 50:
            dim = 25
        for i in range(ceil(width/dim)):
            for j in range(ceil(height/dim)):
                if (i+j)%2 == 0:
                    Graphics.drawRect(image, i*dim, j*dim, dim-1, dim-1, stroke=None, fill="#eeeeee", lineWidth=0)
        return image
    
    def withBackground(image):
        background = Graphics.getBackground(image.width, image.height)
        return Image.alpha_composite(background, image)

    def drawImageInRect(canvas, image, left, top, width, height, border="black"):
        size, = Graphics.getSize(image.width, image.height, (width, height)),
        image = Graphics.withSize(image, (width-2, height-2))
        imageLeft = left + int(width/2 - size[0]/2)
        imageTop = top + int(height/2 - size[1]/2)+1
        canvas.paste(
            image,
            (
                imageLeft+1,
                imageTop+1
            ),
        )

        stroke = border
        Graphics.drawRect(
            canvas,
            imageLeft,
            imageTop,
            size[0],
            size[1],
            stroke=stroke,
            lineWidth=1,
        )

    def drawRect(image, left, top, width, height, stroke="black", fill=None, lineWidth=1):
        ret = ImageDraw.Draw(image)
        shape = [(left, top), (left+width, top+height)]
        ret.rectangle(shape, fill=fill, outline=stroke, width=lineWidth)
    
    def drawText(image, x, y, width, height, text, fill="black", bgColor="white"):
        draw = ImageDraw.Draw(image)

        maxLineLen = 0
        lines = text.split("\n")
        for line in lines:
            maxLineLen = max(maxLineLen, len(line))
        widthFactor = 0.66666
        heightFactor = 1.5
        size = min(
            width / (maxLineLen * widthFactor),
            height / (len(lines) * heightFactor)
        )

        font = ImageFont.truetype(r'./src/fonts/roboto_mono_bold.ttf', size)  
        textWidth = 0
        for line in text.split("\n"):
            textWidth = max(textWidth, draw.textlength(line, font=font))
        left = x-textWidth/2
        top = y-(len(lines))*size/2
        if bgColor is not None:
            Graphics.drawRect(image, left, top+size/10, textWidth, size, None, bgColor)
        draw.text((left, top), text, font=font, fill=fill)

        # draw.text((x, y), text, font=font, align="center", fill=(255, 0, 255))
    
    def scale(image, factor, showGuides=True):
        ret = image.resize(
            (image.width*factor, image.height*factor),
            Image.NEAREST
        )
        if(showGuides):
            for i in range(image.width):
                for j in range(image.height):
                    stroke = "#bbbbbb"
                    if i%5 == 0 and j%5 == 0: stroke = "black"
                    if i%10 == 0 and j%10 == 0: stroke = "red"
                    Graphics.drawRect(ret, i*factor, j*factor, 1, 1, stroke=stroke)
        return ret
    
    def getSize(width, height, size):
        widthRatio = size[0]/width
        heightRatio = size[1]/height
        ratio = min(widthRatio, heightRatio)
        return (int(ratio*width), int(ratio*height))

    def withSize(image, size):
        print("Resizing?")
        resizing = Image.NEAREST
        # if image.width > size[0] or image.height > size[1]:
        #     resizing = Image.BICUBIC
        #     image = Graphics.scale(image, 2, showGuides=False)
        ret = image.resize(
            Graphics.getSize(image.width, image.height, size),
            resizing,
        )
        return ret
    
    def crop(image):
        """ Returns a cropped copy of the image, or None if the image is empty. """
        image = image.convert('RGBA')
        left, right, top, bottom = image.width, 0, image.height, 0
        empty = True
        for i in range(image.width):
            for j in range(image.height):
                _r, _g, _b, a = image.getpixel((i, j))
                if a != 0:
                    left = min(left, i)
                    right = max(right, i)
                    top = min(top, j)
                    bottom = max(bottom, j)
                    empty = False
        if(empty): return None
        image = image.crop((left, top, right+1, bottom+1))
        return image
    
    def withCaption(image, caption, width, height):
        textLength = 30
        caption = "\n".join(wrap(caption, textLength))

        canvas = Image.new('RGBA', (width, height))

        imgWidth = min(width, height)
        
        # draw border
        stroke = "#bbbbbb"
        lineWidth = 1
        Graphics.drawRect(
            canvas,
            1, 1,
            width-2, height-2,
            fill="#ffeeee",
            stroke=stroke,
            lineWidth=lineWidth,
        )
        
        # draw sprite and rect of bounds
        Graphics.drawImageInRect(
            canvas,
            image,
            2, 2,
            imgWidth-4, imgWidth-4
        )

        if width > height:
            textX = imgWidth
            textY = 0
        else:
            textX = 0
            textY = imgWidth
        textWidth = width-textX
        textHeight = height-textY
        Graphics.drawText(
            canvas, 
            textX + textWidth/2,
            textY + textHeight/2,
            textWidth,
            textHeight,
            caption,
            bgColor=None,
        )
        return canvas
    
    def collect(images, pad=0, border="#bbbbbb"):
        if len(images) == 0:
            w = 1000
            h = 100
            image = Image.new('RGBA', (w, h))
            Graphics.drawText(image, w/2, h/2, w, h, "No Images.")
            return image

        imgWidth = images[0].width
        imgHeight = images[0].height
        d = 1.5 # desired aspect ratio
        rowLength = ceil(sqrt(d*imgHeight*len(images)/imgWidth))
        columnCount = ceil(len(images)/rowLength)
        image = Image.new(
            'RGBA',
            (
                imgWidth*rowLength,
                imgHeight*columnCount,
            ),
        )
        index = 0
        canvas = Image.new("RGBA", image.size, (0, 0, 0, 0))
        for i in range(len(images)):
            image = images[i]
            tup = (
                imgWidth * (index % rowLength),
                imgHeight * int(index / rowLength),
            )
            
            # draw sprite and rect of bounds
            Graphics.drawImageInRect(
                canvas,
                Graphics.withBackground(images[i]),
                tup[0]+pad+1, tup[1]+pad+1,
                imgWidth-2*pad-2, imgHeight-2*pad-2,
            )

            index += 1
        return canvas