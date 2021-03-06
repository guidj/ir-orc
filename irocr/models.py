class Document(object):
    def __init__(self, id, text):
        self.id = id
        self.text = text


class RGBHistogram(object):

    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b
        self._dominant_color = None

    @property
    def dominant_rgb_color(self):

        if self._dominant_color is None:
            import operator
            values = zip((self.r, self.g, self.b), ('red', 'green', 'blue'))
            hist, color = max(values, key=operator.itemgetter(0))

            self._dominant_color = color

        return self._dominant_color


class Photo(object):

    def __init__(self, id, exif, address, dicom_info, rgb_histogram, is_low_constrast=False, keypoints=None):
        self.id = id
        self.exif = exif
        self.address = address
        self.dicom_info = dicom_info
        self.rgb_histogram = rgb_histogram
        self.is_low_contrast = is_low_constrast
        self.keypoints = keypoints
