"""
Description
-----------
This script/module contains the functions to parse the pdf for slide numbers and an embedded image to extract participant_id and other identifiers. 
 
Functions
---------
parse_pdf:
    load pdf, split to images/strings/metadata
extract_slide_numbers:
    extract the 6-digit slide no from the pack
extract_slide_info_image:
    ocr on the patient/slide info sticker thumbnail
extract_IDs:
    extracts the PIDs from thumbnails.
format_output:
    basic QA and assemble 

...
"""
import pdfreader
import PIL.ImageOps 
import re
import pandas as pd
from pdfreader import PDFDocument, SimplePDFViewer
import pytesseract

#slides pdf file path

def parse_pdf(fp2):
    """
    loads pdf given as parameter and 
    returns an array of pages and text data, images and inline images within each page.   
    """
    
    print(fp2)

    slides_fp = fp2 
    slides_fd = open(slides_fp, "rb")
    print(slides_fd)
    pdf_doc   = PDFDocument(slides_fd)

    #page iterator
    viewer = SimplePDFViewer(slides_fd)
    PageImages = []
    PageData = []
    PageStrings = []
    PagesInline = []
    PageIndex = 0

    for canvas in viewer:
        print(PageIndex)
        PageImages.append(canvas.images)
        PageStrings.append(canvas.strings)
        PageData.append(canvas.text_content)
        PagesInline.append(canvas.inline_images)
        PageIndex = PageIndex+1
        
    
    return PageImages, PageStrings, PageData, PagesInline


def extract_slide_numbers(PageStrings):
    """
    extracts slide numbers from the Strings in document by matching all the consecutive 6-digit patterns. 
    """
    
    #concatenate all strings to extract slide number - 6 digit string
    allStringsj = sum(PageStrings, [])   
    allStrings = ''.join(allStringsj)
    slide_numbers = re.findall("\d\d\d\d\d\d", allStrings)
    
    return slide_numbers
    
def extract_slide_info_image(PageImages):
    """
    extracts info thumbnails from PageImages list of dictionaries and stores it in a specified folder.  
    """

    thumbnailStrings = []
    PageNo = 0
    
    for Page in PageImages:
        InSlide = 1
        for key in PageImages[PageNo]:
            if (divmod(InSlide,2)[1] == 0): 
                Image = PageImages[PageNo][key]
                pil_image = Image.to_Pillow()
                #extract strings
                thumbnailStrings.append(pytesseract.image_to_string(pil_image))  
                #build path string
                ifp = "/Users/georgiachan/MMX/Manifests/Gs_Greater_Manchester_set/PageNo_"+str(PageNo) + "_" +key +".png"
                ''.join(ifp.split())    #remove white spaces
                print(ifp)
                #optional
                #pil_image.save(ifp)     #write image to directory 
            InSlide = InSlide+1
        PageNo = PageNo+1
    return thumbnailStrings
    
    
def extract_IDs(thumbnailStrings, defaultProvider):
    """
    extracts the PIDs from thumbnails.  
    """
    
    participant_id      = []
    image_file_name     = []
    local_id   = []
    histology_no = []
    No = 0
    
    for label in thumbnailStrings:
        #tr_label = label.strip()
        #print(label)
        tr_label = label.replace(" ", "") #remove extra white spaces
        dot_star_check = re.compile('(?:\\n)+') #remove multiple \n
        tr_label = re.sub(dot_star_check, '£', tr_label)
        #print(No)
        #print(tr_label)
        try:
            local_id_p = re.search('%s(.*)%s' %('[^]*£[|i]*R', '£'), tr_label).group(1)
            local_id_p1 = "R"+local_id_p
        except:
            local_id_p1 = defaultProvider
            local_id_p = defaultProvider
        if not (re.findall("£[CHWw]", tr_label)):
            histology_no_p = "No local ID"
            histology_no_p1 = "No local ID"
        else:
            histology_no_p = re.search('%s(.*)%s' %('£[CHWw]', '[£$]'), tr_label).group(1)
            if not (re.findall("£H", tr_label)):
                if not (re.findall("£[Ww]", tr_label)):
                    histology_no_p1 = "C"+histology_no_p
                else:
                    histology_no_p1 = "W"+histology_no_p
            else:
                histology_no_p1 = "H"+histology_no_p
        
        #print(local_id_p)
        #print(histology_no_p1)
        
        
        participant_id.append(re.findall("\d\d\d\d\d\d\d\d\d", tr_label)[0])
        image_file_name.append(re.findall("\d\d\d\d\d\d\d\d\dPathologyimage", tr_label))
        local_id.append(local_id_p1)
        histology_no.append(histology_no_p1)
        No = No+1
        #print("--")
        
        
        output = pd.DataFrame({'participant_id': participant_id,
                              'image_file_name': image_file_name, 
                              'local_id': local_id, 
                              'histology_no': histology_no })
    return output #participant_id, image_file_name, local_id, histology_no
   
    
    
    



