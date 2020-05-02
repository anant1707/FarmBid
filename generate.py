from io import BytesIO
from docx.shared import Cm
from docxtpl import DocxTemplate, InlineImage
from flask import send_file

def get_context(invdata,contents):
  
    return {
        'invoice_no': invdata[0],
        'date': invdata[1],
        'name': invdata[2],
        'address': invdata[3],
        'total': invdata[4],
        'payment': invdata[5],
        'sname': invdata[6],
        'saddress': invdata[7],
        'row_contents': contents
    }


def from_template(template, signature,invdata,contents):
    target_file = BytesIO()

    template = DocxTemplate(template)
    context = get_context(invdata,contents)  # gets the context used to render the document

    img_size = Cm(7)  # sets the size of the image
    sign = InlineImage(template, signature, img_size)
    context['signature'] = sign  # adds the InlineImage object to the context

    target_file = BytesIO()
    template.render(context)
    template.save(target_file)

    return target_file

def iamcalled(x):
    name=str(x[0])
    with open(name+".docx", "wb") as f:


        document=from_template('InvoiceTpl.docx','signature.png',[x[1],x[4],x[2]+" "+x[3],x[5],float(x[6])*float(x[7]),x[9],x[10]+" "+x[11],x[12]],[{'description':x[8],'quantity':x[6],'rate':x[7],'amount':float(x[6])*float(x[7])}])

        f.write(document.getbuffer())
