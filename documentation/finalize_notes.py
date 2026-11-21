import subprocess, time, os, uno
from com.sun.star.beans import PropertyValue
def pv(n, v): p = PropertyValue(); p.Name, p.Value = n, v; return p
proc = subprocess.Popen(['soffice', '--headless', '--norestore', '--accept=socket,host=localhost,port=2003;urp;'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
for _ in range(60):
    try:
        l = uno.getComponentContext(); r = l.ServiceManager.createInstanceWithContext('com.sun.star.bridge.UnoUrlResolver', l)
        ctx = r.resolve('uno:socket,host=localhost,port=2003;urp;StarOffice.ComponentContext'); break
    except Exception: time.sleep(1)
desk = ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', ctx)
src = 'documentation/Business_Performance_Analysis_Complete_Notes'
doc = desk.loadComponentFromURL('file://' + os.path.abspath(src + '.docx'), '_blank', 0, (pv('Hidden', True),))
idx = doc.getDocumentIndexes(); print('indexes', idx.getCount())
for i in range(idx.getCount()): idx.getByIndex(i).update()
doc.storeToURL('file://' + os.path.abspath(src + '.docx'), (pv('FilterName', 'MS Word 2007 XML'),))
doc.storeToURL('file://' + os.path.abspath(src + '.pdf'), (pv('FilterName', 'writer_pdf_Export'),)); doc.close(True)
try: desk.terminate()
except Exception: pass
proc.terminate()
