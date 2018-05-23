from __future__ import division

import pickle
import csv
import os
import re
import sys
import numpy as np
import xml.etree.ElementTree as et

from pyexcel_xls import save_data
from nltk.corpus import stopwords
from collections import OrderedDict

from Model.Filepath import *
from Model.Document import *
from Model.Pair import *
import gi

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk, Pango

class MainWindow(Gtk.Window):
	def __init__(self):
		Gtk.Window.__init__(self, title="Plagiarism Detection With Merging Context Seeds")
		self.set_border_width(10)
		self.set_size_request(200, 100)
		self.set_resizable(False)
		self.connect("delete-event", Gtk.main_quit)

		#Layout
		vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
		self.add(vbox)

		##Doc1
		grid1 = Gtk.Grid()
		doc1_l = Gtk.Label(label="Document 1 : ")
		grid1.add(doc1_l)

		self.doc1_e = Gtk.Entry()
		self.doc1_e.set_text("D:\Cuppyzh\_new-tugas-akhir\_TA 2.Program\Dataset\susp\suspicious-document01700.txt")
		self.doc1_e.set_width_chars(100)
		grid1.attach_next_to(self.doc1_e, doc1_l, Gtk.PositionType.RIGHT, 1, 2)
		vbox.pack_start(grid1, True, True, 0)
		#vbox.pack_start(self.doc1_e, True, True, 0)

		##Doc1
		grid2 = Gtk.Grid()
		doc2_l = Gtk.Label(label="Document 2 : ")
		grid2.add(doc2_l)

		self.doc2_e = Gtk.Entry()
		self.doc2_e.set_text("D:\Cuppyzh\_new-tugas-akhir\_TA 2.Program\Dataset\src\source-document01914.txt")
		self.doc2_e.set_width_chars(100)
		grid2.attach_next_to(self.doc2_e, doc2_l, Gtk.PositionType.RIGHT, 1, 2)
		vbox.pack_start(grid2, True, True, 0)
		#vbox.pack_start(self.doc1_e, True, True, 0)

		#Check Button
		grid3 = Gtk.Grid()
		check_l = Gtk.Label(label="Datasets ")
		self.checkbox = Gtk.CheckButton()
		grid3.add(self.checkbox)

		grid3.attach_next_to(check_l, self.checkbox, Gtk.PositionType.RIGHT, 1,2 )
		vbox.pack_start(grid3, True, True, 0)
#		grid3.attach_next_to()

		#Button
		button = Gtk.Button(label="Submit")
		button.connect("clicked", self.submit)
		vbox.pack_start(button, True, True, 0)

	def submit(self, widget):
		print(self.doc1_e.get_text())
		print(self.doc2_e.get_text())

		try : 
			file1 = io.open(self.doc1_e.get_text())
			file2 = io.open(self.doc2_e.get_text())


		except:
			print("No File Found")
			WarningWindow = WarningBox()
			WarningWindow.show_all()
			Gtk.main()
			WarningWindow.destroy()

		print("Processing")
		self.p = Pair()
		self.p.guiPair(self.doc1_e.get_text(), self.doc2_e.get_text())
		data = self.p.GUI()
		
		if len(data[2]) == 0:
			print("No Plag Case")
			noplag = NoPlagCase()
			noplag.show_all()
			Gtk.main()
			noplag.destroy()
		else:
			print("Tampilin")

			susp = DocumentBox(data[0],"susp", data[2])
			susp.show_all()

			susp = DocumentBox(data[1],"src", data[2])
			susp.show_all()

			doc = data[3]
			log = LogBox(doc)
			log.show_all()

			Gtk.main()
			print("Done")

		if self.checkbox.get_active() == True:
			print("SINI")
			self.p.susp.guiLog()
			self.p.src.guiLog()
		else:
			print("SANA")
			pass

class DocumentBox(Gtk.Window):
	def __init__(self, doc, type, r):

		Gtk.Window.__init__(self, title=doc['name'])
		self.set_resizable(False)

		self.set_border_width(10)

		#Layout
		vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
		self.add(vbox)

		grid = Gtk.Grid()
		label = Gtk.Label(label="Text : ")
		
		scrolledwindow = Gtk.ScrolledWindow()
		scrolledwindow.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.ALWAYS)
		grid.attach(scrolledwindow, 1, 1, 1, 1)

		textview = Gtk.TextView()
		textview.set_wrap_mode(Gtk.WrapMode.CHAR)
		scrolledwindow.set_size_request(720,720)
		textbuffer = textview.get_buffer()
		#textbuffer.set_text(doc['text'])
		

		errorTag = textview.get_buffer().create_tag("BOLD", weight=Pango.Weight.BOLD)

		textbuffer.set_text(doc['text'])

		#APPLY TAG

		for item in r:
			if type == "src":
				start = textview.get_buffer().get_iter_at_offset(item[0])
				end = textview.get_buffer().get_iter_at_offset(item[1])
				textview.get_buffer().apply_tag(errorTag, start, end)
			else :
				start = textview.get_buffer().get_iter_at_offset(item[2])
				end = textview.get_buffer().get_iter_at_offset(item[3])
				textview.get_buffer().apply_tag(errorTag, start, end)



		scrolledwindow.add(textview)
		vbox.pack_start(grid, True, True, 0)

		self.connect("delete-event", Gtk.Window.destroy)

class LogBox(Gtk.Window):
	def __init__(self, text):

		Gtk.Window.__init__(self, title='LOG')
		self.set_resizable(False)

		self.set_border_width(10)

		vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=50)
		self.add(vbox)

		grid = Gtk.Grid()
		label = Gtk.Label(label="Text : ")

		scrolledwindow = Gtk.ScrolledWindow()
		scrolledwindow.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.ALWAYS)
		grid.attach(scrolledwindow, 1, 1, 1, 1)

		textview = Gtk.TextView()
		textview.set_wrap_mode(Gtk.WrapMode.CHAR)
		scrolledwindow.set_size_request(720,720)
		textbuffer = textview.get_buffer()
		#textbuffer.set_text(doc['text'])
		

		errorTag = textview.get_buffer().create_tag("BOLD", weight=Pango.Weight.BOLD)

		textbuffer.set_text(text)

		scrolledwindow.add(textview)
		vbox.pack_start(grid, True, True, 0)

		self.connect("delete-event", Gtk.Window.destroy)


class WarningBox(Gtk.Window):
	def __init__(self):
		Gtk.Window.__init__(self, title="!!!!!")
		self.set_border_width(10)
		self.set_resizable(False)

		#Layout
		vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
		self.add(vbox)

		#Grid
		grid = Gtk.Grid()
		label = Gtk.Label(label="Either document is not found")
		grid.add(label)

		button = Gtk.Button(label="Ok")
		button.connect("clicked", Gtk.main_quit)
		grid.attach_next_to(button, label, Gtk.PositionType.BOTTOM, 1,2 )

		vbox.add(grid)
		self.connect("delete-event", Gtk.Window.destroy)

	def close(self, widget):
		pass

class NoPlagCase(Gtk.Window):
	def __init__(self):
		Gtk.Window.__init__(self, title="!!!!!")
		self.set_border_width(10)
		self.set_resizable(False)

		#Layout
		vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
		self.add(vbox)

		#Grid
		grid = Gtk.Grid()
		label = Gtk.Label(label="There is no plagiarism case found")
		grid.add(label)

		button = Gtk.Button(label="Ok")
		button.connect("clicked", Gtk.Window.destroy)
		grid.attach_next_to(button, label, Gtk.PositionType.BOTTOM, 1,2 )

		vbox.add(grid)
		self.connect("delete-event", Gtk.Window.destroy)

	def close(self, widget):
		pass

class waitBox(Gtk.Window):
	def __init__(self):
		Gtk.Window.__init__(self, title="Wait")
		self.set_border_width(10)
		self.set_resizable(False)

		#Layout
		vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
		self.add(vbox)

		#Grid
		grid = Gtk.Grid()
		label = Gtk.Label(label="Wait while document is beign processed")
		grid.add(label)

		vbox.add(grid)


window = MainWindow()

window.connect("delete-event", Gtk.main_quit)
window.show_all()
Gtk.main()
Gtk.main_quit()