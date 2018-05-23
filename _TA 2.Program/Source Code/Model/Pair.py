from __future__ import division

import csv
import os
import re
import sys
import numpy as np
import pickle
import xml.etree.ElementTree as et

from pyexcel_xls import save_data
from nltk.corpus import stopwords
from collections import OrderedDict

from Model.Filepath import *
from Model.Document import *


class Pair :

	par = 7
	minLength = 15

	def __init__(self):
		pass

	def guiPair(self, susp, src):
		self.susp = Document("x", susp)
		self.susp.run()

		self.src = Document("x", src)
		self.src.run()


		self.getCaseS()

		self.raiseIndexMap()
		#print("3")
		self.clearPassageReferences()
		#print("4")
		self.singleLinkageClustering2()
		#print("5")
		self.filterCluster()
		#print("6")
		self.getDetectionR()
		#print("8")
		

		self.rDetectS2()

	def newPair(self, susp, src):

		self.susp = Document("susp",susp)
		self.susp.run()

		self.src = Document("src",src)
		self.src.run()

		self.run()

	def loadDump(self, susp, src):
		"""
		Load file from dump file which is already preprocessing to avoid long execution tine
		"""

		path = Filepath()

		file = open(path.suspDump+susp+".txt", 'r')
		self.susp = pickle.load(file)
		file.close()

		file = open(path.srcDump+src+".txt", 'r')
		self.src = pickle.load(file)
		file.close()
		self.run()

	def loadDumps(self, susp, src):
		"""
		Load file from dump file which is already preprocessing to avoid long execution tine
		"""

		path = Filepath()

		file = open(path.suspDump2+susp+".txt", 'rb')
		print path.suspDump2+susp+".txt"
		self.susp = pickle.load(file)
		file.close()

		file = open(path.srcDump2+src+".txt", 'rb')
		self.src = pickle.load(file)
		file.close()
		self.run()

	def getCaseS(self):
		"""
		Find justification of pair document from dataset.
		This justification used to validate if the output of this program is equal from the dataset, which said the justification is true. Other false
		"""
		
		self.s = []

		try:
			self.susp.docName = self.susp.docName[-28:]
			self.src.docName = self.src.docName[-24:]
			print self.susp.docName
			print self.src.docName
			self.xmlname = self.susp.docName.replace(".txt","") + "-" + self.src.docName.replace(".txt","") + ".xml"
		except:
			print "adsasd"
			pass
		print self.xmlname

		path = Filepath()

		tree = None
		typePlag = ""

		try :
			tree = et.parse(path.noPlagiarismPath+self.xmlname)
			typePlag = "No Plagiarism"
		except :
			pass

		try :
			tree = et.parse(path.noObfuscationPath+self.xmlname)
			typePlag = "No Obfuscation"
		except :
			pass

		try :
			tree = et.parse(path.randomObfuscationPath+self.xmlname)
			typePlag = "Random Obfuscation"
		except :
			pass

		try :
			tree = et.parse(path.translationObfuscationPath+self.xmlname)
			typePlag = "Translation Obfuscation"
		except :
			pass

		try :
			tree = et.parse(path.summaryObfuscationPath+self.xmlname)
			typePlag = "Summary Obfuscation"
		except :
			pass
		try:
			root = tree.getroot()
		except:
			pass

		if typePlag == "No Obfuscation" or typePlag == "Random Obfuscation" or typePlag == "Translation Obfuscation":
			src_length = -1
			src_offset = -1
			susp_length = -1
			susp_offset = -1

			for item in root.iter('feature'):
				src_length = int(item.attrib['source_length'])
				src_offset = int(item.attrib['source_offset'])
				susp_length = int(item.attrib['this_length'])
				susp_offset = int(item.attrib['this_offset'])

				#self.s.append([src_offset, src_length, susp_offset, susp_length])
				self.s.append([src_offset, src_length+src_offset, susp_offset, susp_length+susp_offset])
		elif typePlag == "Summary Obfuscation":

			for item in root.iter('feature'):
				if str(item.attrib['name']) == 'plagiarism':
					src_length = -1
					src_offset = -1
					susp_length = -1
					susp_offset = -1

					src_length = int(item.attrib['source_length'])
					src_offset = int(item.attrib['source_offset'])
					susp_length = int(item.attrib['this_length'])
					susp_offset = int(item.attrib['this_offset'])

					#self.s.append([src_offset, src_length, susp_offset, susp_length])
					self.s.append([src_offset, src_length+src_offset, susp_offset, susp_length+susp_offset])

		self.typePlag = typePlag

	def raiseIndexMap(self):
		"""
		Raise feature map suspicous x source document
		Susp x Src

		var result
		plotMap = [Susp X Src] biner of 1
		"""

		np.set_printoptions(threshold=np.nan, linewidth=np.nan)

		self.passageReference = []
		#self.plotMap = np.zeros((len(self.susp.fmap), len(self.src.fmap)))

		for i, item1 in enumerate(self.susp.fmap):
			for j, item2 in enumerate(self.src.fmap):
				if item1[3] == item2[3] :
					#self.plotMap[i][j] = 1
					self.passageReference.append([item1, item2])

	def clearPassageReferences(self):
		"""
		Remove multiple passage Refrence that has same value

		Caused by 1 word that have more than 1 same feature between source document and suspicious document
		"""

		newPassageReferences = []

		for i,item in enumerate(self.passageReference):
			Flag = True
			for j,item2 in enumerate(self.passageReference):
				if i != j :
					if item == item2:
						Flag = False
			if Flag == True:
				newPassageReferences.append(item)

		self.passageReference = newPassageReferences

	def distP(self, P1, P2):
		"""
		Calculate distance between 2 passage (P1 and P2) in same document
		"""
		
		calc = P1[1] - P2[1]
		calc2 = P1[0] - P2[0]

		if calc < 0:
			calc = calc * -1

		if calc < 0:
			calc2 = calc2 * -1

		return calc

	def perimeter(self, R):
		"""
		Calculate total wide of Passage Reference (R). This formula make an R is rectangular in Cartesian Product to find distance meassure 
		"""

		return ( 2 * (R[0][1] - R[0][0]) ) + ( 2 * (R[1][1] - R[1][0]) )

	def distR(self, R1, R2):
		"""
		Calculate distance between Passage Reference (R1 and R2)
		"""

		atas = (2 * self.distP(R1[0], R2[0])) + (2 * self.distP(R1[1], R2[1]))
		bawah = 1 + (self.perimeter(R1)) + (self.perimeter(R2))

		return atas / bawah

	def singleLinkageClustering2(self):
		"""
		Single Linkage Clustering
		"""

		if self.passageReference <= 1:
			self.cluster = self.passageReference
		else:

			cluster = []

			for item in self.passageReference:
				row = []
				row.append(item)
				cluster.append(row)

			while True:
				try:
					mindist = self.distR(cluster[0][0], cluster[1][0])
					c1 = 0
					c2 = 1
				except:
					break

				for ind1, item1 in enumerate(cluster):
					for ind2, item2 in enumerate(cluster):

						if ind1 != ind2:

							for i in item1:
								for j in item2:
									calc = self.distR(i,j)
									#print(calc)
									if calc < mindist:
										mindist = calc
										c1 = ind1
										c2 = ind2

				if mindist >= self.par:
					
					break
				else:

					cluster[c1] = cluster[c1] + cluster[c2]
					cluster.pop(c2)

			self.cluster = cluster

	def filterCluster(self):
		"""
		Remove any cluster that have item less than 15 words
		"""

		newCluster = []

		for item in self.cluster:

			if len(item) >= self.minLength:
				newCluster.append(item)

		self.filteredCluster = newCluster

	def mergeJoinCluster(self):

		while True:
			try:
				c1 = 0
				c2 = 1
				item = self.r[0]
				item2 = self.r[1]
				slices = self.slice(item[0],item[1],item2[0],item2[1]) + self.slice(item[0],item[1],item2[0],item2[1])
			except:
				print sys.exc_info()[0]
				break

			for i,item in enumerate(self.r):
				for j,item2 in enumerate(self.r):
					if item != item2:
						s1 = self.slice(item[2],item[3],item2[2],item2[3])
						s2 = self.slice(item[0],item[1],item2[0],item2[1])
						#print("SLICES")
						#print(s1[0]+s2[0])
						if (s1[0] + s2[0]) > 0 and slices > (s1[0] + s2[0]):
							#print("SLICES")
							#print(s1[0]+s2[0])
							c1 = i
							c2 = j

			if (s1[0]+s2[0]) == 0 :
				break

			#newR
			if self.r[c1][0] < self.r[c2][0]:
				minSrc = self.r[c1][0]
			else:
				minSrc = self.r[c2][0]

			if self.r[c1][1] > self.r[c2][1]:
				maxSrc = self.r[c1][1]
			else:
				maxSrc = self.r[c2][1]

			if self.r[c1][2] < self.r[c2][2]:
				minSusp = self.r[c1][2]
			else:
				minSusp = self.r[c2][2]

			if self.r[c1][3] > self.r[c2][3]:
				maxSusp = self.r[c1][3]
			else:
				maxSusp = self.r[c2][3]

			newR = [minSrc, maxSrc, minSusp, maxSusp]
			self.r[c1] = newR
			self.r.pop(c2)
			#self.filteredCluster[c1] = self.filteredCluster[c1] + self.filteredCluster[c2]


	def getDetectionR(self):
		"""
		Parse any cluster that fulfill the requirement to set of Detection R

		var result
		array of [StartSrc, EndSrc, StartSusp, EndSusp]
		"""

		self.r = []

		for item in self.filteredCluster:

			minSusp = item[0][0][0]
			maxSusp = item[0][0][1]

			minSrc = item[0][1][0]
			maxSrc = item[0][1][1]

			for item2 in item:
				if minSusp > item2[0][0]:
					minSusp = item2[0][0]

				if maxSusp < item2[0][1]:
					maxSusp = item2[0][1]

				if minSrc > item2[1][0]:
					minSrc = item2[1][0]

				if maxSrc < item2[1][1]:
					maxSrc = item2[1][1]

			self.r.append([minSrc, maxSrc, minSusp, maxSusp])

	def slice(self, s1, s2, r1, r2):
		#TP,FP,FN
		if r1 < s1 and r2 > s2:
			return [( 2 * (s2 - s1)), 2 * ((r2-s2) + (s1-r1)), 0]
		elif r1 >= s1 and r2 <= s2:
			return [( 2 * (r2 - r1)), 0, 2 * ((r1-s1) + (s2-r2))]
		elif r1 < s1 and r2 > s1 and r2 <= s2:
			return [( 2 * (r2 - s1)), 2 * (s1-r1), 2 * (s2-r2)]
		elif r1 > s1 and r1 <= s2 and r2 > s2:
			return [( 2 * (s2 - r1)), 2 * (r2-s2), 2 * (r1-s1)]
		else:
			return [0,0,0]

	def rDetectS2(self):
		tpfp = 0
		tp = 0
		tpfn = 0
		tn = 0
		fn = 0
		slicess = 0

		self.pr = len(self.src.text) * len(self.susp.text)
		try:
			for item in self.s:
				tpfn = tpfn + ( 2 * (item[1] - item[0])) + ( 2 * (item[3] - item[2]))
		except:
			tpfn = 0

		try:
			for item in self.r:
				tpfp = tpfp + ( 2 * (item[1] - item[0])) + ( 2 * (item[3] - item[2]))
		except:
			tpfp = 0
		"""
		for item in self.r:
			for item2 in self.r:
				if item!=item2:
					s1 = self.slice(item[2],item[3],item2[2],item2[3])
					s2 = self.slice(item[0],item[1],item2[0],item2[1])
					if s1 != 0 and s2 != 0:
						slicess = s2[0] - s1[0]
		"""

		if (len(self.r) > 0):
			self.s = sorted(self.s, key=lambda x: x[0])
			self.r = sorted(self.r, key=lambda x: x[0])

			self.rs = []
			self.tp = []

			for item in self.s:
				for item2 in self.r:
					c1 = self.slice(item[0],item[1],item2[0],item2[1])
					c2 = self.slice(item[2],item[3],item2[2],item2[3])

					if c1[0] != 0 and c2[0] != 0 :
						tp = tp + c1[0] + c2[0]
						print("TP"+str(c1[0]+c2[0]))
						self.tp.append([c1,c2])
						self.rs.append([item, item2])

					if c1[2] != 0 and c2[0] !=0:
						fn = fn + c1[2] + c2[2]

		if slicess < 0:
			slicess = slicess * -1

		#tp = tp - slicess

		print("LAST")
		print(tp)
		self.norm = [tp,tpfp,tpfn]

		try:
			prec = tp/tpfp
		except:
			prec = "DIV 0"

		try:
			rec = tp/tpfn
		except:
			rec = "DIV 0"

		try:
			f1 = (2*(tp/tpfp)*(tp/tpfn))/((tp/tpfp)+(tp/tpfn))
		except:
			f1 = "DIV 0"

		self.normf1 = [prec,rec,f1]

		tp = tp
		fp = tpfp - tp
		fn = tpfn - tp
		tn = self.pr - (tpfn + fp)

		self.perf = [tp,fp,fn,tn] #TP / TPFP / TPFN

		try:
			prec = tp/(tp+fp)
		except:
			prec = tp

		try:
			rec = tp/(tp+fn)
		except:
			rec = tp

		try:
			f1 = (2 * prec * rec)/(prec+rec)
		except:
			f1 = tp

		self.f1 = [prec,rec,f1]

		#R

		temp = tp
		tp = tn
		tn = temp

		temp = fp
		fp = fn
		fn = temp

		self.rperf = [tp,fp,fn,tn] #TP / TPFP / TPFN

		try:
			prec = tp/(tp+fp)
		except:
			prec = tp

		try:
			rec = tp/(tp+fn)
		except:
			rec = tp

		try:
			f1 = (2 * prec * rec)/(prec+rec)
		except:
			f1 = tp

		self.rf1 = [prec,rec,f1]

	def rDetectS(self):

		pr = len(self.susp.text) * len(self.src.text)
		tp = 0
		fn = 0
		tpfn = 0
		tpfp = 0
		tn = 0
		prec = 0
		recall = 0
		f1 = 0
		invtp = 0
		invtpfp=0
		invtpfn=0
		invp=0
		invr=0
		invf1=0
		microRec=0
		microPrec=0
		microF1=0
		fp = 0

		for item in self.s:
			tpfn = tpfn + ( 2 * (item[1] - item[0])) + ( 2 * (item[3] - item[2]))


		for item in self.r:
			tpfp = tpfp + ( 2 * (item[1] - item[0])) + ( 2 * (item[3] - item[2]))

		if len(self.r) > 0:

			self.s = sorted(self.s, key=lambda x: x[0])
			self.r = sorted(self.r, key=lambda x: x[0])

			self.rs = []
			self.tp = []

			self.pr = pr 
			invtp = 0
			tp = 0

			for item in self.s:
				for item2 in self.r:
					c1 = self.slice(item[0],item[1],item2[0],item2[1])
					c2 = self.slice(item[2],item[3],item2[2],item2[3])

					if c1 != 0 and c2 != 0 :

						fp = fp + c1[1] + c1[1]
						fn = fn + c1[2] + c2[2]
						tp = tp + c1[0] + c2[0]

						self.tp.append([c1,c2])
						self.rs.append([item, item2])
						##Hitung Inverse
						invtp = invtp + ( c1[0] + c2[0] )

		else:
			pass

		invtpfp = pr - tpfp
		invtpfn = pr - tpfn

		try:
			prec = tp/(tp+fp)
		except:
			prec = 0

		try:
			recall = tp/(tp+fn)
		except:
			recall = 0


		try:
			f1 = (2 * recall * prec) / (recall+prec)
		except:
			f1 = 0

		invtp = pr  - (tpfp + tpfn - invtp)
		try :
			invp = invtp / (invtpfp)
		except:
			invp = 0

		try :
			invr = invtp / (invtpfn)
		except:
			invr = 0	

		try:
			invf1 = 2 * invr * invp / (invr + invp)
		except:
			invf1 = 0

		try:
			microPrec = (tp + invtp) / (tp + invtp + tpfp + invtpfp)
		except:
			microPrec = 0

		try:
			microRec = (tp + invtp) / (tp + invtp + tpfn + invtpfn)
		except:
			microRec = 0  

		try:
			microF1 = ( 2 * microRec * microPrec) / (microRec + microPrec)
		except:
			microF1 = 0 

		try:
			tn = pr - ((tpfn-tp) + (tpfp-tp) + tp )
		except:
			tn = 0

			#TP / FN / FP / TN
			
		#print(tpfn)
		#print(tpfp)
		#print(tp)

		self.perf = [tp,fn,fp,tn]
		self.f1 = [prec,recall,f1]
		self.rperf = [invtp,invtpfp-invtp,invtpfn-invtp,tp]
		self.rf1 = [invp,invr,invf1]
		self.microf1 = [microPrec, microRec,microF1]
		self.pr = pr


	def evaluation(self):
		"""
		Evaluate between set Case S and set Detection R

		return F-Measure
		"""

		#Preparation
		self.s = sorted(self.s, key=lambda x: x[0])
		self.r = sorted(self.r, key=lambda x: x[0])

		size = len(self.s)

		if len(self.r) > size:
			size = len(self.r)

		if size == 0:
			size = 1

		#self.eval = [self.susp.docName, self.src.docName, ' ', self.f1[0], self.f1[1], self.f1[2], self.f1[3], self.f1[4], self.f1[5]]
		self.eval = [self.susp.docName, self.src.docName, ' ', self.f1[0], self.f1[1], self.f1[2]]


	def run(self):
		"""
		Balance on the all thing

		do all the thing
		"""
		#print("1")
		self.getCaseS()
		#print("2")
		self.raiseIndexMap()
		#print("3")
		self.clearPassageReferences()
		#print("4")
		self.singleLinkageClustering2()
		#print("5")
		self.filterCluster()
		#print("6")
		self.getDetectionR()



		self.mergeJoinCluster()
		#rint("7")
		self.rDetectS2()
		#print("8")
		self.evaluation()
		#self.rDetectS() MUST NO BEEN CALLED
		#self.evaluation()
		#self.output()

		#Output FIle

	def output(self):

		print(self.susp.docName+ " " + self.src.docName)
		f = open('Log/Eval-'+self.typePlag+'/'+self.susp.docName+' '+self.src.docName+'.txt', 'w')

		print(self.susp.docName+ " " + self.src.docName)
		print("Type of Plag : "+self.typePlag)

		print("\nParameter Used")
		print("Threshold Relevance : "+str(self.src.refThreshold))
		print("Max Distance : "+str(self.par))
		print("Min Cluster size : "+str(self.minLength))

		print("\nSet of Case S : ")

		for item in self.s:
			print(item)

		print("\nSet of Detection R : ")

		for item in self.r:
			print(item)

		print("\nEvaluation")

		print("True Positive : "+str(self.f1[0]))
		print("TPFN : "+str(self.f1[1]))
		print("TPFP : "+str(self.f1[2]))
		print("Prec : "+str(self.f1[3]))
		print("Recall : "+str(self.f1[4]))
		print("F1 : "+str(self.f1[5]))
		#pickle.dump(self, f)
		f.close()

	def GUI(self):
		print("HOHO")

		susp = {}
		susp['name'] = self.susp.docName
		susp['text'] = self.susp.text

		src = {}
		src['name'] = self.src.docName
		src['text'] = self.src.text

		data = []
		data.append(susp)
		data.append(src)
		data.append(self.r)

		log = ""
		log+= "Document 1 Name : "+self.susp.docName
		log+= "\nDocument 2 Name : "+self.src.docName

		if self.typePlag != "":
			log+= "\nDataset Plagiarism Type : "+self.typePlag

		else:
			log+= "\nDataset Plagiarism Type : -"

		log+= "\n\nSize of Filtered Clsuster : "+str(len(self.filteredCluster))
		log+= "\nFiltered Cluster"

		temp = ""
		for item in self.filteredCluster:
			temp+="\n"+str(item)+"\n"

		log+=temp

		temp = "\n\nSet of S"
		for item in self.s:
			temp+="\n"+str(item)

		log+=temp

		temp = "\n\nSet of R"
		for item in self.r:
			temp+="\n"+str(item)

		log+=temp

		log+="\n"
		log+="\nPerfomansi"
		log+="\nPrecision : "+str(self.f1[0])
		log+="\nRecall : "+str(self.f1[1])

		log+="\nF1 : "+str(self.f1[2])
#		log+="\n"+str(self.f1)

		data.append(log)

		return data