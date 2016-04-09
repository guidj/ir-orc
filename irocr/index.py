import os
import tempfile

import requests
import xml.etree.cElementTree as ET

import config
import logger
import models


class SolrIndex(object):
    def __init__(self):
        pass

    @property
    def cfg(self):
        cfg = config.get('solr')

        if not cfg:
            raise RuntimeError('Solr config not found')

        assert 'host' in cfg
        assert 'port' in cfg

        return cfg

    def add_documents(self, documents):
        assert isinstance(documents, list)

        root = ET.Element('add')

        for document in documents:
            assert isinstance(document, models.Document)

            doc = ET.SubElement(root, 'doc')

            ET.SubElement(doc, 'field', name='id').text = str(document.id)
            ET.SubElement(doc, 'field', name='content').text = document.content

        tree = ET.ElementTree(root)

        tmpfile = os.path.join(tempfile.tempdir, tempfile.mktemp('.tmp'))
        tree.write(tmpfile)

        with open(tmpfile, 'r') as fp:
            data = ''.join(fp.readlines())

        os.remove(tmpfile)
        cfg = self.cfg

        url = 'http://{}:{}/solr/{}/update'.format(
            cfg['host'],
            cfg['port'],
            'papers'
        )

        response = requests.post(url, data=data, params={'commit': 'true'}, headers={'Content-type': 'text/xml'})
        logger.Logger.info(response.status_code)

    def add_photos(self, photos):
        assert isinstance(photos, list)

        root = ET.Element('add')

        for photo in photos:
            assert isinstance(photo, models.Photo)

            doc = ET.SubElement(root, 'doc')

            ET.SubElement(doc, 'field', name='id').text = str(photo.id)
            ET.SubElement(doc, 'field', name='exif').text = photo.exif
            ET.SubElement(doc, 'field', name='address').text = photo.address
            ET.SubElement(doc, 'field', name='dicom').text = photo.dicom_info
            ET.SubElement(doc, 'field', name='dominant_rgb_color').text = photo.rgb_histogram.dominant_rgb_color
            ET.SubElement(doc, 'field', name='color.r').text = str(photo.rgb_histogram.r)
            ET.SubElement(doc, 'field', name='color.g').text = str(photo.rgb_histogram.g)
            ET.SubElement(doc, 'field', name='color.b').text = str(photo.rgb_histogram.b)
            ET.SubElement(doc, 'field', name='is_low_constrast').text = str(photo.is_low_contrast)

            if photo.keypoints is not None:
                ET.SubElement(doc, 'field', name='keypoints.x').text = str(photo.keypoints[:, 0])
                ET.SubElement(doc, 'field', name='keypoints.y').text = str(photo.keypoints[:, 1])

        tree = ET.ElementTree(root)

        tmpfile = os.path.join(tempfile.tempdir, tempfile.mktemp('.tmp'))
        tree.write(tmpfile)

        with open(tmpfile, 'r') as fp:
            data = ''.join(fp.readlines())

        os.remove(tmpfile)
        cfg = self.cfg

        url = 'http://{}:{}/solr/{}/update'.format(
            cfg['host'],
            cfg['port'],
            'photos'
        )

        response = requests.post(url, data=data, params={'commit': 'true'}, headers={'Content-type': 'text/xml'})
        logger.Logger.info(response.status_code)
