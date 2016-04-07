import os
import tempfile

import requests
import xml.etree.cElementTree as ET

import config
import logger


class Document(object):
    def __init__(self, id, content, exif, address, dicom_info):
        self.id = id
        self.content = content
        self.exif = exif
        self.address = address
        self.dicom_info = dicom_info


class SolrIndex(object):
    def __init__(self):
        pass

    @property
    def url(self):
        cfg = config.get('solr')

        if not cfg:
            raise RuntimeError('Solr config not found')

        url = 'http://{}:{}/solr/{}/update'.format(
            cfg['host'],
            cfg['port'],
            cfg['core']
        )

        return url

    def add(self, documents):
        assert isinstance(documents, list)

        root = ET.Element('add')

        for document in documents:
            assert isinstance(document, Document)

            doc = ET.SubElement(root, 'doc')

            ET.SubElement(doc, 'field', name='id').text = str(document.id)
            ET.SubElement(doc, 'field', name='content').text = document.content
            ET.SubElement(doc, 'field', name='exif').text = document.exif
            ET.SubElement(doc, 'field', name='address').text = document.address
            ET.SubElement(doc, 'field', name='dicom').text = document.dicom_info

        tree = ET.ElementTree(root)

        tmpfile = os.path.join(tempfile.tempdir, tempfile.mktemp('.tmp'))
        tree.write(tmpfile)

        with open(tmpfile, 'r') as fp:
            data = ''.join(fp.readlines())

        os.remove(tmpfile)
        response = requests.post(self.url, data=data, params={'commit': 'true'}, headers={'Content-type': 'text/xml'})
        logger.Logger.info(response.status_code)
