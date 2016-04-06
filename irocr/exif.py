from exifread import process_file


class EXIFReader:
    def __init__(self):
        pass

    @staticmethod
    def read_exif_tags(filepath):
        f = open(filepath, 'rb')
        tags = process_file(f)
        return tags
