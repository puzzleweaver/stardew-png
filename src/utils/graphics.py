
from PIL import Image, ImageDraw, ImageFont
from textwrap import wrap

class Graphics:
    """This class collects all of the image rendering used in the sprite unpacker."""

    def drawRect(image, left, top, width, height, stroke="black", fill=None, lineWidth=1):
        ret = ImageDraw.Draw(image)
        shape = [(left, top), (left+width, top+height)]
        ret.rectangle(shape, fill=fill, outline=stroke, width=lineWidth)
    
    def drawText(image, x, y, width, height, text):
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
        draw.text((left, top), text, font=font, fill="black")

        # draw.text((x, y), text, font=font, align="center", fill=(255, 0, 255))
    
    def scale(image, factor):
        ret = image.resize(
            (image.width*factor, image.height*factor),
            Image.NEAREST
        )
        if(factor > 3):
            for i in range(image.width):
                for j in range(image.height):
                    stroke = "#bbbbbb"
                    if i%5 == 0 and j%5 == 0: stroke = "black"
                    Graphics.drawRect(ret, i*factor, j*factor, 1, 1, stroke=stroke)
        return ret
    
    def collect(filenames, images, manifest, selected):
        imgWidth = 200
        rowLength = 10
        image = Image.new(
            'RGB',
            (
                imgWidth*rowLength,
                2*imgWidth*(int(len(filenames)/rowLength)+1),
            ),
        )
        index = 0
        canvas = Image.new("RGBA", image.size, (0, 0, 0, 0))
        for i in range(len(images)):
            thumbnail = Graphics.scale(images[i], 3)
            filename = filenames[i]
            tagString = manifest.getFileTagString(filename)
            tup = (
                imgWidth * (index % rowLength),
                2*imgWidth * int(index / rowLength),
            )
            canvas.paste(thumbnail, (tup[0], tup[1]))

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

            # draw border
            stroke = "#bbbbbb"
            lineWidth = 1
            if filename in selected:
                stroke = "red"
                lineWidth = 3
            Graphics.drawRect(
                canvas, 
                tup[0]+2,
                tup[1]+2, 
                imgWidth - 5, 
                imgWidth*2 - 5,
                stroke=stroke,
                lineWidth=lineWidth
            )
            
            index += 1
        return canvas