

def read_aadhar(image_file):
    """ Read aadhar file and returns dictonary of contents
    Parameters:
        image_file - The barcode file 
     """
    from PIL import Image
    import zbarlight
    image = Image.open(image_file)
    image.load()
    codes = zbarlight.scan_codes('qrcode', image)
    import xml.etree.ElementTree as ET
    tree = ET.fromstringlist(codes)
    # Returns dict of aadhar card data
    return tree.attrib
