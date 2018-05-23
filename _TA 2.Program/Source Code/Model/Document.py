import csv
import os
import re
import io
import shutil
import sys
import pickle

from nltk.corpus import stopwords

from Model.Filepath import *

class Document:


	refThreshold = 4

	def __init__(self, docType, docName):
		"""
		Document initialization : Doc Name and Doc Type
		"""

		self.docType = docType
		self.docName = docName

	def loadFile(self):
		"""
		1. Load file 
		2. Parse loaded file into 1 string variable
		"""

		path = Filepath()

		if self.docType == "x":
			file = io.open(self.docName, encoding="utf8")
		else:
			file = io.open(path.type[self.docType] + self.docName, encoding="utf8")

		self.lines = file.readlines()
		self.text = ""

		for item in self.lines:

			temp = item
			temp = temp.replace("\n"," ") #Replace 'white space' with 'space' ; a bit pre-processing data

			self.text = self.text + temp

		self.text = self.text.lower() #Lower Casing ; a bit pre-processing data
		self.text = self.text.encode('utf-8') #Preventin error, change text to utf-8

		file.close()

	def generateCharacterMap(self):
		"""
		Map every character in text into character map.
		Known which character appear where.
		x = (c, i) ; c = character, i = index

		var result
		characterMap = array of [index, character]
		"""

		self.characterMap = []

		for index,item in enumerate(self.text):
			self.characterMap.append([index, item])

	def removeNonAlphanumericCharacter(self):
		"""
		Remove every character in character map which character is categorized as Non Alphanumeric character
		"""

		nonAlphaNumericCharacter = set("`~!@#$%^&*()_+-={}|[]\:\"<>?;',./'\xc2")
		temp = []

		for item in self.characterMap:
			if not any(( c in nonAlphaNumericCharacter ) for c in item[1]):
				temp.append(item)

		self.cleanCharacterMap = temp

	def generateWordMap(self):
		"""
		Map every word meet in text into word map.
		Know which word appear where.
		w1 = (xi~xj,i)

		var result
		wordMap = array of [index, endIndex, wordString, word]
		word : finite set of character map elemen; word = []
		index : index of first character map elemen on word
		"""

		self.wordMap = []
		word = []
		itt = 0

		while True:
			
			try:
				if self.cleanCharacterMap[itt][1] == ' ':

					index = word[0][0]
					endIndex = word[len(word)-1][0]

					wordString = ""

					for item in word:
						wordString = wordString + item[1]

					self.wordMap.append([index, endIndex, wordString, word])
					word = []

					while self.cleanCharacterMap[itt][1] == ' ':
						itt += 1

						if itt >= len(self.cleanCharacterMap):
							break

				else:

					word.append(self.cleanCharacterMap[itt])
					itt += 1



				if itt >= len(self.cleanCharacterMap):
					wordString = ""
					
					for item in word:
						wordString = wordString + item[1]
					self.wordMap.append([index, endIndex, wordString, word])
					break
			except IndexError:
				if len(word) > 0:
					index = word[0][0]
					endIndex = word[len(word)-1][0]

					wordString = ""

					for item in word:
						wordString = wordString + item[1]

					self.wordMap.append([index, endIndex, wordString, word])
					word = []

				break


	def removeStopWords(self):
		"""
		Removing stop words from word map, make 'clean word map'
		"""

		self.cleanWordMap = []
		st = stopwords.words("english")

		for item in self.wordMap:
			flag = True

			for item2 in st:

				item2str = item2.encode('utf-8')
				
				if item[2] == item2str:

					flag = False
					break

			if flag == True:
				self.cleanWordMap.append(item)

	def nSkipwordBigram(self):
		"""
		Generate feature from clean word map.
		f = Wb,Wi : i = b ~ 1--4

		var result
		featureMap = array of [index, endIndex, stringWord, f1, f2, f3, f4]
		"""

		self.featureMap = []

		for index,item in enumerate(self.cleanWordMap):
			newItem = item[0:3]
			for i in range(1, 5): #1~4
				if index - i < 0:
					newItem.append(['*', item[2]])
				else:
					newItem.append([self.cleanWordMap[index-i][2], item[2]])

			self.featureMap.append(newItem)

	def featureSelection(self):
		"""
		Remove feature fx if fx appear more than 4 time in feature map

		Plot all fature to 1 dimmensional array of [f]
		Find which feature is not allowed if |[fx]| > 4

		var result

		fmap = featureMap

		newfmap = array of [index, endIndex, stringWord, f] :: f1~f4 separated by their own index
		"""

		self.fmap = []

		for item in self.featureMap:
			for i in range(1, 5): #1~4
				self.fmap.append([item[0], item[1], item[2], item[2+i]])

		self.newfmap = []

		for item1 in self.fmap:
			ct = 0
			for item2 in self.fmap:
				if item1[3] == item2[3]:
					ct += 1

			if ct <= self.refThreshold:
				self.newfmap.append(item1)

	def guiLog(self):
		print("MASUK")

		target = open('Log/RUN-LOG-'+self.docName+'.txt','w')
		target.truncate()
		target.write("Document Name : "+self.docName)

		target.close()

	def run(self):
		"""
		Balance on the all thing

		do all the thing
		"""
		
		self.loadFile()
		self.generateCharacterMap()
		self.removeNonAlphanumericCharacter()
		self.generateWordMap()
		self.removeStopWords()
		self.nSkipwordBigram()
		self.featureSelection()
