from Model.Document import *
from Model.Pair import *
from Model.Filepath import *

from pyexcel_xls import save_data

import io
import sys
import time


print("Running Driver - Eval")

start_time = time.time()

sys.stdout = open('Log/Log-Eval.txt', 'w')

path = Filepath()
file = io.open(path.pairs)
listPair = file.readlines()

for i in range(1,1828):

	if len(str(i)) == 1:
		wildcard = "0000"+str(i)
	elif len(str(i)) == 2:
		wildcard = "000"+str(i)
	elif len(str(i)) == 3:
		wildcard = "00"+str(i)
	elif len(str(i)) == 4:
		wildcard = "0"+str(i)
	elif len(str(i)) == 5:
		pass
		
	d = Document("susp", "suspicious-document"+wildcard+".txt")
	d.run()

	f = open('../Dataset/susp-dump2/'+d.docName+".txt","wb")
	pickle.dump(d, f)
	f.close()