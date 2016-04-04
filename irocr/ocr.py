from PIL import Image
import sys

import pyocr
import pyocr.builders
import pyocr.tesseract


class OCRReader(object):

    def __init__(self):
        tools = pyocr.get_available_tools()
        if len(tools) == 0:
            self.tool = None
        else:
            self.tool = tools[0]

    def read_image(self, filepath, lang='eng'):

        if not self.tool:
            raise RuntimeError('No OCR tool found')

        text = self.tool.image_to_string(
            Image.open(filepath),
            lang=lang,
            builder=pyocr.builders.TextBuilder()
        )

        return text

#TODO: delete
if __name__ == '__main__':

    filepath = sys.argv[1]
    reader = OCRReader()
    text = reader.read_image(filepath)

    print(text)
