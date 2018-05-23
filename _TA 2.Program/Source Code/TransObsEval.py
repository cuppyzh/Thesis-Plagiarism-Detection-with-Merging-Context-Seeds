from Model.Document import *
from Model.Pair import *
from Model.Filepath import *

from pyexcel_xls import save_data

import io
import sys
import time

#TP / FN / FP / TN
		#self.perf = [tp,tpfn-tp,tpfp-tp,tn]
		#self.f1 = [prec,recall,f1]
		#self.rperf = [invtp,pr-tpfn,pr-tpfp,tp]
		#self.rf1 = [invp,invr,invf1]
		#self.microf1 = [microPrec, microRec,microF1]

print("Running Driver - Translation Obfuscation")

start_time = time.time()

path = Filepath()
file = io.open(path.pairsTransObs)
listPair = file.readlines()

pairs = []
forEval = []
data = OrderedDict()
datas = []
datas.append(["Suspicious Document", "Source Document", " ", "TP", "FN", "FP", "TN", "Prec", "Rec", "F1"," ", "TP'", "FN'", "FP'", "TN'", "Prec'", "Rec'", "F1'","","PR"])

ignoreList = ['suspicious-document00111.txt source-document02990.txt']
passPair = 'suspicious-document00000.txt source-document00000.txt'

Flag = False
ct = -5

for i, item in enumerate(reversed(listPair)):
	p = Pair()

	if Flag == False:
		if item[:28]+" "+item[29:-1] == passPair:
			ct = i
			Flag = True
		else:
			print((item[:28]+" "+item[29:-1])+" -- passed")
	else:

		if Flag == True:
			print(item[:28]+" "+item[29:-1])
			p.loadDump(item[:28], item[29:-1])
			#THIS IS FOR TESTING
			#p = Pair("suspicious-document00006.txt", "source-document02227.txt")
			#e = p.evaluation()


			datas.append([p.eval[0], p.eval[1], "", p.perf[0], p.perf[1], p.perf[2], p.perf[3], p.f1[0], p.f1[1], p.f1[2], "", p.rperf[0], p.rperf[1], p.rperf[2], p.rperf[3], p.rf1[0], p.rf1[1], p.rf1[2], "", p.pr," ",p.norm[0],p.norm[1],p.norm[2]])

			data.update({'Sheet 1': datas})
			save_data("Translation Obfuscation.xls", data)

print(len(pairs))
print("--- %s seconds ---" % (time.time() - start_time))