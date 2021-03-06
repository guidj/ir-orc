import dicom
import dicom.errors
import exifread
import logger
import skimage
import skimage.io
import skimage.exposure
import skimage.feature
import skimage.color
import time
import requests
import json


def convert_exif_dms_to_decimal(dms_array, ref):
    assert isinstance(dms_array, list)
    assert isinstance(ref, basestring)

    decimal_number = ((float(dms_array[0].num) / float(dms_array[0].den)) +
                      (float(dms_array[1].num) / (float(dms_array[1].den) * 60.0)) +
                      (float(dms_array[2].num) / (float(dms_array[2].den) * 3600.0)))
    if ref.upper() == 'S' or ref.upper() == 'W':
        decimal_number *= -1
    return decimal_number


class EXIFReader(object):
    def __init__(self):
        pass

    @staticmethod
    def read_exif_tags(filepath):
        with open(filepath, 'rb') as fp:
            data = exifread.process_file(fp)
        return data

    @staticmethod
    def retrieve_location(tags):
        lat = convert_exif_dms_to_decimal(tags['GPS GPSLatitude'].values, tags['GPS GPSLatitudeRef'].values)
        lon = convert_exif_dms_to_decimal(tags['GPS GPSLongitude'].values, tags['GPS GPSLongitudeRef'].values)
        time.sleep(2)

        location = requests.get('http://nominatim.openstreetmap.org/reverse?'
                                'lat={}&lon={}&format=json&accept-language=en'.format(
            str(round(lat, 4)),
            str(round(lon, 4))
        )).content

        location = json.loads(location)

        return location['display_name']

    def retrieve_exif_information_strings(self, filepath):
        tags = self.read_exif_tags(filepath)
        exif_string = ''.join([k + ': ' + str(v) + '\n' for k, v in tags.items() if k != 'JPEGThumbnail'])

        if all(k in tags for k in ('GPS GPSLatitude', 'GPS GPSLatitudeRef',
                                   'GPS GPSLongitude', 'GPS GPSLongitudeRef')):
            address = self.retrieve_location(tags)
        else:
            address = ''
        return exif_string, address


def read_dicom_file_meta(filename):
    try:
        with open(filename, 'rb') as fp:
            data = dicom.read_file(fp)
        return str(data)
    except dicom.errors.InvalidDicomError as err:
        logger.Logger.warning('DICOM data could not be retrieved: {}'.format(err))
        return ''


def rgb_histogram(filename, normalize=True):
    try:
        image = skimage.io.imread(filename)
        imagef = skimage.img_as_float(image)

    except IOError as err:
        logger.Logger.warning('rgb_histogramm could not be retrieved: {}'.format(err))
        rhs, ghs, bhs = '', '', ''
        return rhs, ghs, bhs

    r, g, b = imagef[:, :, 0].copy(), imagef[:, :, 1].copy(), imagef[:, :, 2].copy()
    rh, gh, bh, = map(skimage.exposure.histogram, (r.copy(), g.copy(), b.copy()))
    rhs, ghs, bhs = map(lambda x: sum(x[0] * x[1]), (rh, gh, bh))

    if normalize:
        s = sum((rhs, ghs, bhs))
        rhs, ghs, bhs = map(lambda x: x / s, (rhs, ghs, bhs))

    return rhs, ghs, bhs


def is_low_contrast(filename):
    try:
        image = skimage.io.imread(filename)
        return skimage.exposure.is_low_contrast(image)
    except Exception as err:
        logger.Logger.warning('contrast info could not be retrieved: {}'.format(err))
        return ''


def censure(filename):
    """
    The CENSURE feature detector is a scale-invariant center-surround detector (CENSURE) that claims to outperform
    other detectors and is capable of real-time implementation.
    """
    try:
        detector = skimage.feature.CENSURE()
        image = skimage.color.rgb2gray(skimage.io.imread(filename))
        detector.detect(image)
        return detector.keypoints
    except Exception as err:
        logger.Logger.warning('keypoints could not be retrieved: {}'.format(err))
        return ''
