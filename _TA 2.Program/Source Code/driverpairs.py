from Model.Document import *
from Model.Pair import *
from Model.Filepath import *

from pyexcel_xls import save_data

import io
import sys
import time

print("Running Driver")

start_time = time.time()

try:
	path = Filepath()
	file = io.open(sys.argv[1]) #File Path Pairs File
	listPair = file.readlines()

	pairs = []
	forEval = []
	data = OrderedDict()
	datas = []
	datas.append(["Suspicious Document", "Source Document", " ", "TP", "FN", "FP", "TN", "Prec", "Rec", "F1"," ", "TP'", "FN'", "FP'", "TN'", "Prec'", "Rec'", "F1'","","PR"])

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

				datas.append([p.eval[0], p.eval[1], "", p.perf[0], p.perf[1], p.perf[2], p.perf[3], p.f1[0], p.f1[1], p.f1[2], "", p.rperf[0], p.rperf[1], p.rperf[2], p.rperf[3], p.rf1[0], p.rf1[1], p.rf1[2], "", p.pr])

				data.update({'Sheet 1': datas})
				save_data("Log List Proses List.xls", data)

	print(len(pairs))
	print("--- %s seconds ---" % (time.time() - start_time))

except:
	print "Unexpected error:", sys.exc_info()[0]