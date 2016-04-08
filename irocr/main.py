import sys
import os

import ocr
import meta
import index
import logger


def usage():
    info = """
    irocr path [-r] [-f formats]

    Where
        - path: is a path to a file or directory containing images
        - r: is a flag to read images recursively from directory
        - f: is a parameter, with the file formats to be read. By default, system looks for png, gif, tif
    """

    print(info)


def read_images(files):
    ocr_reader = ocr.OCRReader()
    exif_reader = meta.EXIFReader()

    for file in files:
        logger.Logger.info('Reading image file [%s]', file)

        text = ocr_reader.read_image(file)

        exif_info, address = exif_reader.retrieve_exif_information_strings(file)

        dicom_info = meta.read_dicom_file_meta(file)

        dirname = os.path.dirname(file)
        id = '{}-{}'.format(os.path.split(dirname)[-1], os.path.basename(file))

        yield index.Document(id, text, exif_info, address, dicom_info)


if __name__ == '__main__':

    if len(sys.argv) < 2:
        usage()
        sys.exit(1)

    path = None
    recursive = False
    formats = ['.gif, .png', '.tif']
    ir = index.SolrIndex()

    for i in range(1, len(sys.argv)):
        if i == 1:
            path = sys.argv[i]
        else:

            if sys.argv[i] == '-r':
                recursive = True
            elif sys.argv[i] == '-f':
                if len(sys.argv) > i + 1:
                    usage()
                    raise RuntimeError('Missing parameter: -f')

                formats = (sys.argv[i + 1]).split(',')
                shape = lambda x: x if str(x).startswith('.') else ''.join(('.', x))
                formats = [shape(f) for f in formats]
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

    documents = read_images(files)

    for doc in documents:
        ir.add([doc])
