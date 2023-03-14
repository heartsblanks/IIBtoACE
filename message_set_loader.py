from xml.etree import ElementTree as ET

class MessageSetLoader:
    @staticmethod
    def loadMessageSet(inputFilePath):
        # Load the message set file and return the root element
        return ET.parse(inputFilePath).getroot()
