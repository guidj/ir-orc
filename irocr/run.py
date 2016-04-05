import sys
import os
import ocr
import index
if __name__ == '__main__':
    directory = sys.argv[1]
    tif_files = []
    documents = []
    ocr_reader = ocr.OCRReader()
    doc_index = index.Index()
    for path, subdirs, files in os.walk(directory):
        for filename in files:
            if filename.endswith('.tif'):
                tif_files.append(os.path.join(path, filename))

    for tif_file in tif_files:
        documents.append(ocr_reader.read_image(tif_file))

    doc_index.add_documents(documents)
