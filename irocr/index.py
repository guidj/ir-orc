import requests
import xml.etree.cElementTree as ET


class Document(object):

    def __init__(self, id, content):
        self.id = id
        self.content = content


class Index(object):

    def __init__(self):
        pass

    def add_documents(self, documents):
        assert isinstance(documents, list)

        root = ET.Element('add')

        for document in documents:

            assert isinstance(document, Document)

            doc = ET.SubElement(root, 'doc')

            ET.SubElement(doc, 'field', name='id').text = str(document.id)
            ET.SubElement(doc, 'field', name='content').text = document.content

            # for k, v in document.fields.iteritems():
            #     ET.SubElement(doc, 'field', name=k).text = v

        tree = ET.ElementTree(root)
        tree.write('payload.xml')

        # TODO: send payload to http://localhost:8983/solr/update?commit=true

#TODO: delete
if __name__ == '__main__':

    data = [
        Document(1, 'Some document'),
        Document(2, 'Another document')
    ]

    index = Index()
    index.add_documents(documents=data)
