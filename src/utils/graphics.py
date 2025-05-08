
from math import ceil
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

    def drawImageInRect(canvas, image, left, top, width, height):
        size, = Graphics.getSize(image.width, image.height, (width, height)),
        image = Graphics.withSize(image, (width, height))
        canvas.paste(
            image,
            (
                left + int(width/2 - size[0]/2),
                top + int(height/2 - size[1]/2),
            ),
        )

    def drawRect(image, left, top, width, height, stroke="black", fill=None, lineWidth=1):
        ret = ImageDraw.Draw(image)
        shape = [(left, top), (left+width, top+height)]
        ret.rectangle(shape, fill=fill, outline=stroke, width=lineWidth)
    
    def drawText(image, x, y, width, height, text, fill="black"):
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
        top = y-size/2
        if not '\n' in text:
            Graphics.drawRect(image, left, top+size/10, textWidth, size, None, "white")
        draw.text((left, top), text, font=font, fill=fill)

        # draw.text((x, y), text, font=font, align="center", fill=(255, 0, 255))
    
    def scale(image, factor, dim=1):
        ret = image.resize(
            (image.width*factor, image.height*factor),
            Image.NEAREST
        )
        if(factor > 3):
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
        resizing = Image.NEAREST
        if image.width > size[0] or image.height > size[1]:
            resizing = Image.BICUBIC
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
    
    def collect(filenames, images, manifest):
        imgWidth = 300
        pad = 5
        rowLength = int((3 * len(filenames)) ** 0.5) + 1
        image = Image.new(
            'RGBA',
            (
                imgWidth*rowLength,
                2*imgWidth*ceil(len(filenames)/rowLength),
            ),
        )
        index = 0
        canvas = Image.new("RGBA", image.size, (0, 0, 0, 0))
        for i in range(len(images)):
            filename = filenames[i]
            tagString = "\n".join(
                wrap(" ".join(manifest.getFileTags(filename)), 13),
            ).replace(" ", ",")
            tup = (
                imgWidth * (index % rowLength),
                2*imgWidth * int(index / rowLength),
            )
            
            # draw border
            stroke = "#bbbbbb"
            lineWidth = 1
            Graphics.drawRect(
                canvas,
                tup[0]+pad,
                tup[1]+pad,
                imgWidth - 2*pad,
                imgWidth*2 - 2*pad,
                stroke=stroke,
                lineWidth=lineWidth
            )
            
            # draw sprite and rect of bounds
            Graphics.drawImageInRect(
                canvas,
                Graphics.withBackground(images[i]),
                tup[0]+2*pad, tup[1]+2*pad,
                imgWidth-4*pad, imgWidth-4*pad,
            )

            suffix = filename.split("/")[-1]
            lines = [ f"{suffix}:" ] + tagString.split("\n")
            Graphics.drawText(
                canvas, 
                tup[0] + imgWidth/2,
                tup[1] + imgWidth,
                imgWidth,
                imgWidth,
                "\n".join(lines),
            )

            index += 1
        return canvas