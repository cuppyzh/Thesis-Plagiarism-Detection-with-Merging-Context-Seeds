from __future__ import division

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

class Pre:
	def __init__(self, doc):
		pass