import ffs
from ffs.contrib import archive

# with ffs.Path.temp() as tmp:
zipfile = archive.ZipPath('/tmp/my.zip')
content1 = zipfile/'content.txt'
content1 << "These are some contents"

zipfile/'my.csv' << "number,letter\n1,a\n2,b"
zipfile << ('second.csv', "number,letter\n3,c\n4,d")
