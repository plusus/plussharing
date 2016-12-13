import sys, os, PrivateForm, PublicForm, ScriptShare
from PySide.QtCore import *
from PySide.QtGui import *


#********#
#**Main**#
#********#
application = QApplication([])
myForm = None
scriptObject = ScriptShare.ScriptShare(sys.argv[2], sys.argv[3])

if str(sys.argv[1]) == 'Personnal':
    myForm = PrivateForm.PrivateForm(scriptObject)
elif str(sys.argv[1]) == 'Public':
    myForm = PublicForm.PublicForm(scriptObject)
else:
    print ("We are sorry, but the first argument received is wrong. It must be Private or Public depending on the sharing mode that you want.")
    print("Received : " + str(sys.argv[1]))

sys.exit(application.exec_())