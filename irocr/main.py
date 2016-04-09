import sys
import os

import ocr
import meta
import index
import models
import logger


def usage():
    info = """
    irocr [-r] [-f formats] [-i] [-s] path

    Where
        - path: is a path to a file or directory containing images
        - r: is a flag to read images recursively from directory
        - f: is a parameter, with the file formats to be read. By default, system looks for png, gif, tif, jpg
        - i: is a flag to read photographs
        - s: is a flag to read scanned documents

        Either the -i or the -s flags must be present
    """

    print(info)


def read_photos(files):
    exif_reader = meta.EXIFReader()

    for file in files:
        logger.Logger.info('Reading image file [%s]', file)

        exif_info, address = exif_reader.retrieve_exif_information_strings(file)

        dicom_info = meta.read_dicom_file_meta(file)

        dirname = os.path.dirname(file)
        id = '{}-{}'.format(os.path.split(dirname)[-1], os.path.basename(file))

        r, g, b = meta.rgb_histogram(file)
        rgb_hist = models.RGBHistogram(r, g, b)
        is_low_contrast = meta.is_low_contrast(file)
        keypoints = meta.censure(file)

        yield models.Photo(id, exif_info, address, dicom_info, rgb_hist, is_low_contrast, keypoints)


def read_scans(files):
    ocr_reader = ocr.OCRReader()

    for file in files:
        logger.Logger.info('Reading image file [%s]', file)

        text = ocr_reader.read_image(file)

        dirname = os.path.dirname(file)
        id = '{}-{}'.format(os.path.split(dirname)[-1], os.path.basename(file))

        yield models.Document(id, text)


def main(operation, files):

    if operation == '-s':

        documents = read_scans(files)

        for doc in documents:
            ir.add_documents([doc])

    elif operation == '-i':

        photos = read_photos(files)

        for photo in photos:
            ir.add_photos([photo])


if __name__ == '__main__':

    argc = len(sys.argv)
    if argc < 2:
        usage()
        sys.exit(1)

    path = None
    recursive = False
    operation = None
    formats = ['.gif', '.png', '.tif', '.jpg']
    ir = index.SolrIndex()

    for i in range(1, argc):
        if i == argc - 1:
            path = sys.argv[i]
        else:

            if sys.argv[i] == '-r':
                recursive = True
            elif sys.argv[i] == '-f':
                if argc < i + 1:
                    usage()
                    raise RuntimeError('Missing parameter: -f')

                formats = (sys.argv[i + 1]).split(',')
                shape = lambda x: x if str(x).startswith('.') else ''.join(('.', x))
                formats = [shape(f) for f in formats]
            elif sys.argv[i] == '-i':
                if operation is None:
                    operation = sys.argv[i]
                else:
                    usage()
                    if operation == sys.argv[i]:
                        raise RuntimeError('Flags {} is repeated', sys.argv[i])
                    else:
                        raise RuntimeError('Flags {} and {} cannot be used at the same time',
                                           operation, sys.argv[i])
            elif sys.argv[i] == '-s':
                if operation is None:
                    operation = sys.argv[i]
                else:
                    usage()
                    if operation == sys.argv[i]:
                        raise RuntimeError('Flags {} is repeated', sys.argv[i])
                    else:
                        raise RuntimeError('Flags {} and {} cannot be used at the same time',
                                           operation, sys.argv[i])
            else:
                usage()
                raise RuntimeError('Unknown parameter {}'.format(sys.argv[i]))

    files = []
    if recursive:
        if os.path.isdir(path):

            for dirname, _, file_list in os.walk(path):
                for file in file_list:
                    filename = os.path.join(dirname, file)
                    if any(map(filename.endswith, formats)):
                        files.append(filename)
        else:
            if any(map(path.endswith, formats)):
                files.append(path)
            else:
                raise RuntimeError('Unsupported file [{}]'.format(path))
    else:

        if not os.path.isfile(path):
            usage()
            raise RuntimeError(
                '-r was not used, and {} is not a file'.format(path)
            )
        else:
            files.append(path)

    main(operation, files)

    # TODO: schema.xml for `papers` and `photos`
