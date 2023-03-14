from lxml import etree


class DfdlModelGenerator:
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
        dataTypeOverride,
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

    def get_field_type(self, element):
        # Determine the DFDL data type for a message set element
        fieldType = self.mrmToDfdlDataTypeMapping.get(element.get("type"))

        if fieldType is None:
            if self.dataTypeOverride is not None:
                fieldType = self.dataTypeOverride
            else:
                raise Exception(f"No mapping found for MRM data type: {element.get('type')}")

        return fieldType

    def add_message_set_element_to_dfdl_model(self, element, dfdlParentElement):
        # Add a message set element to the DFDL model
        if element.tag == "xs:element":
            dfdlElement = self.create_dfdl_element(element)
            dfdlParentElement.append(dfdlElement)

        elif element.tag == "xs:complexType":
            if self.complexTypeName is not None:
                dfdlComplexType = etree.Element("dfdl:complexType", nsmap=self.NSMAP)
                dfdlComplexType.attrib["name"] = self.complexTypeName
            else:
                dfdlComplexType = dfdlParentElement

            for childElement in element:
                self.add_message_set_element_to_dfdl_model(childElement, dfdlComplexType)

            if self.complexTypeName is not None:
                dfdlParentElement.append(dfdlComplexType)

    def create_dfdl_element(self, element):
        # Create a DFDL element from a message set element
        dfdlElement = etree.Element("dfdl:element", nsmap=self.NSMAP)
        dfdlElement.attrib["name"] = element.get("name")
        dfdlElement.attrib["type"] = self.get_field_type(element)

        if element.get("minOccurs") is not None:
            dfdlElement.attrib["minOccurs"] = element.get("minOccurs")

        if element.get("maxOccurs") is not None:
            dfdlElement.attrib["maxOccurs"] = element.get("maxOccurs")

        if self.namespacePrefix is not None:
            dfdlElement.attrib[f"xmlns:{self.namespacePrefix}"] = self.targetNamespace

        dfdlElement.append(self.create_annotation("IBM Message Modeling Tool Element", element))
        return dfdlElement

    def createProperty(self, propertyName, propertyValue):
        # Create a DFDL property element
        dfdlProperty = etree.Element("dfdl:property", nsmap=self.NSMAP)
        dfdlProperty.attrib["name"] = propertyName
        dfdlProperty.attrib["value"] = propertyValue
        return dfdlProperty

    def createAnnotation(self, name, value):
        annotation = etree.Element("xsd:annotation", nsmap=self.NSMAP)
        documentation = etree.Element("xsd:documentation", nsmap=self.NSMAP)
        documentation.text = value
        annotation.append(documentation)

        appInfo = etree.Element("xsd:appinfo", nsmap=self.NSMAP)
        appInfo.attrib["source"] = "http://www.ibm.com/dfdl/annotation"
        appInfo.text = f"<dfdl:IBMAnnotation name=\"{name}\" value=\"{value}\"/>"
        annotation.append(appInfo)

        return annotation


