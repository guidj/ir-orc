import PIL.Image
import pyocr
import pyocr.builders
import pyocr.tesseract
import logger

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

        try:
            text = self.tool.image_to_string(
                PIL.Image.open(filepath),
                lang=lang,
                builder=pyocr.builders.TextBuilder()
            )
            return text

        except:
            logger.Logger.warning('OCR could not be executed')
            return ''
