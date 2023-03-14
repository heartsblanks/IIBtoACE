from lxml import etree


class DFDLModelGenerator:
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

    def getFieldType(self, element):
        # Determine the DFDL data type for a message set element
        fieldType = self.mrmToDfdlDataTypeMapping.get(element.get("type"))

        if fieldType is None:
            if self.dataTypeOverride is not None:
                fieldType = self.dataTypeOverride
            else:
                raise Exception(f"No mapping found for MRM data type: {element.get('type')}")

        return fieldType

    def addMessageSetElementToDfdlModel(self, element, dfdlParentElement):
        # Add a message set element to the DFDL model
        if element.tag == "xs:element":
            dfdlElement = self.createDfdlElement(element)
            dfdlParentElement.append(dfdlElement)

        elif element.tag == "xs:complexType":
            if self.complexTypeName is not None:
                dfdlComplexType = etree.Element("dfdl:complexType", nsmap=self.NSMAP)
                dfdlComplexType.attrib["name"] = self.complexTypeName
            else:
                dfdlComplexType = dfdlParentElement

            for childElement in element:
                self.addMessageSetElementToDfdlModel(childElement, dfdlComplexType)

            if self.complexTypeName is not None:
                dfdlParentElement.append(dfdlComplexType)

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
    def generateDfdlModel(self, messageSet):
        # Create a new DFDL message model
        dfdlModel = etree.Element("dfdl:defineFormat", nsmap=self.NSMAP)
        dfdlModel.attrib["name"] = self.modelName
        dfdlModel.attrib["targetNamespace"] = self.targetNamespace

        # Add the DFDL properties and annotations
        dfdlModel.append(self.createProperty("parser.maxOccursUnbounded", str(self.maxOccursUnbounded)))
        dfdlModel.append(self.createProperty("parser.fieldNamingConvention", self.fieldNamingConvention))
        dfdlModel.append(self.createProperty("output.textOutputCharacterEncoding", "UTF-8"))
        dfdlModel.append(self.createProperty("output.checkConstraints", "true"))
        dfdlModel.append(self.createProperty("output.escaping", "true"))
        dfdlModel.append(self.createProperty("output.textPadCharacter", " "))
        dfdlModel.append(self.createAnnotation("IBM Message Modeling Tool Version", self.getMessageSetVersion(messageSet)))
        dfdlModel.append(self.createAnnotation("IBM Message Modeling Tool File", self.getMessageSetFilePath(messageSet)))
        dfdlModel.append(self.createAnnotation("IBM Message Modeling Tool Generated DFDL Model", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

        # Add the root element to the DFDL model
        dfdlRootElement = self.createDfdlElement(
            element=messageSet,
            dfdlParentElement=etree.Element("dfdl:complexType", nsmap=self.NSMAP),
            isRootElement=True,
            elementName=self.rootElementName,
        )
        dfdlModel.append(dfdlRootElement)

        # Return the DFDL model
        return dfdlModel

