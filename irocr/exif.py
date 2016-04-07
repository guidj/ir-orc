from geopy.geocoders import Nominatim
import exifread


def convert_exif_dms_to_decimal(dms_array, ref):
    assert isinstance(dms_array, list)
    assert isinstance(ref, basestring)

    decimal_number = ((float(dms_array[0].num) / float(dms_array[0].den)) +
                      (float(dms_array[1].num) / (float(dms_array[1].den) * 60.0)) +
                      (float(dms_array[2].num) / (float(dms_array[2].den) * 3600.0)))
    if ref.upper() == ('S' or 'W'):
        decimal_number *= -1
    return decimal_number


class EXIFReader(object):
    def __init__(self):
        self.geolocator = Nominatim()

    @staticmethod
    def read_exif_tags(filepath):
        with open(filepath, 'rb') as fp:
            data = exifread.process_file(fp)
        return data

    def retrieve_location(self, tags):
        lat = convert_exif_dms_to_decimal(tags['GPS GPSLatitude'].values, tags['GPS GPSLatitudeRef'].values)
        lon = convert_exif_dms_to_decimal(tags['GPS GPSLongitude'].values, tags['GPS GPSLongitudeRef'].values)
        location = self.geolocator.reverse((lat, lon))
        return location

    def retrieve_exif_information_strings(self, filepath):
        tags = self.read_exif_tags(filepath)
        exif_string = exifread.make_string(tags)

        if all(k in tags for k in ('GPS GPSLatitude', 'GPS GPSLatitudeRef',
                                   'GPS GPSLongitude', 'GPS GPSLongitudeRef')):
            address = self.retrieve_location(tags).address
        else:
            address = ''
        return exif_string, address
