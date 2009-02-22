import urllib
import xml.dom.minidom as dom

def loadXml(url):
    """Read url and return XML dom contents"""
    try:
        filehandle = None
        filehandle = urllib.urlopen(url)
        data = filehandle.read()
        return dom.parseString(data)
    finally:
        if (filehandle): filehandle.close()

def writeXml(doc, filename):
    f = open(filename, "w")
    doc.writexml(f)
    f.close()

def createDocument():
    return dom.Document()

def appendChild(doc, parent, tagName, text=None):
    child = doc.createElement(tagName)
    if (text):
        textChild = doc.createTextNode(text)
        child.appendChild(textChild)
    parent.appendChild(child)
    return child

def validateDocument(doc, name=None):
    """Validate document contains named root element, return root"""
    root = doc.documentElement
    if (not root or (name and root.tagName != name)):
        raise StandardError, "XML document does not contain root element '%s'" % name
    return root

def getChildData(parentNode, childNS, childName, attrName=None, isRequired=True):
    """Find named child of parent, return contents or attribute value"""
    childNodes = parentNode.getElementsByTagNameNS(childNS, childName)
    if (len(childNodes) != 1):
        if (isRequired):
            raise StandardError, "XML node %s does not contain child %s" % (parentNode.tagName, childName)
        else:
            return None
    childNode = childNodes[0]
    if (attrName):
        return childNode.getAttribute(attrName)
    else:
        return childNode.firstChild.wholeText