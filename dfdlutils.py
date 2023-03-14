from xml.etree import ElementTree as ET
from xml.dom import minidom
from lxml import etree
from datetime import datetime

class DFDLUtils:
    NSMAP = {
        "dfdl": "http://www.ogf.org/dfdl/dfdl-1.0/",
        "xsd": "http://www.w3.org/2001/XMLSchema",
    }

    def __init__(
        self,
        modelName,
        targetNamespace,
        fieldNamingConvention,
        maxOccursUnbounded,
        mrmToDfdlDataTypeMapping,
        dataTypeOverride=None,
        complexTypeName=None,
        rootElementName=None,
        namespacePrefix=None,
    ):
        self.modelName = modelName
        self.targetNamespace = targetNamespace
        self.fieldNamingConvention = fieldNamingConvention
        self.maxOccursUnbounded = maxOccursUnbounded
        self.mrmToDfdlDataTypeMapping = mrmToDfdlDataTypeMapping
        self.dataTypeOverride = dataTypeOverride
        self.complexTypeName = complexTypeName
        self.rootElementName = rootElementName
        self.namespacePrefix = namespacePrefix

    def createDfdlElement(self, element):
        # Create a DFDL element from a message set element
        dfdlElement = etree.Element("dfdl:element", nsmap=self.NSMAP)
        dfdlElement.attrib["name"] = element.get("name")
        dfdlElement.attrib["type"] = self.getFieldType(element)

        if element.get("minOccurs") is not None:
            dfdlElement.attrib["minOccurs"] = element.get("minOccurs")

        if element.get("maxOccurs") is not None:
            dfdlElement.attrib["maxOccurs"] = element.get("maxOccurs")

        if self.namespacePrefix is not None:
            dfdlElement.attrib[f"xmlns:{self.namespacePrefix}"] = self.targetNamespace

        dfdlElement.append(self.createAnnotation("IBM Message Modeling Tool Element", element))
        return dfdlElement

    def createProperty(self, name, value):
        # Create a DFDL property
        dfdlProperty = etree.Element("dfdl:property", nsmap=self.NSMAP)
        dfdlProperty.attrib["name"] = name
        dfdlProperty.attrib["value"] = value
        return dfdlProperty

    def createAnnotation(self, label, value):
        # Create a DFDL annotation
        dfdlAnnotation = etree.Element("dfdl:annotation", nsmap=self.NSMAP)
        dfdlAppInfo = etree.Element("dfdl:appinfo", nsmap=self.NSMAP)
        dfdlLabel = etree.Element("dfdl:label", nsmap=self.NSMAP)
        dfdlLabel.text = label
        dfdlValue = etree.Element("dfdl:value", nsmap=self.NSMAP)

        if isinstance(value, ET.Element):
            dfdlValue.text = ET.tostring(value).decode("utf-8")
        else:
            dfdlValue.text = str(value)

        dfdlAppInfo.append(dfdlLabel)
        dfdlAppInfo.append(dfdlValue)
        dfdlAnnotation.append(dfdlAppInfo)
        return dfdlAnnotation

    def getFieldType(self, element):
        # Determine the DFDL data type for a message set element
        fieldType = self.mrmToDfdlDataTypeMapping.get(element.get("type"))

        if fieldType is None:
            if self.dataTypeOverride is not None:
                fieldType = self.dataTypeOverride
            else:
                raise Exception(f"No mapping found for MRM data type: {element.get('type')}")

        return fieldType
