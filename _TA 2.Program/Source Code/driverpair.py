from Model.Document import *
from Model.Pair import *
from Model.Filepath import *
from sys import argv
from pyexcel_xls import save_data

import io
import sys
import time

print("Running Driver")

sys.stdout = open('Log-Driver-Pair.txt', 'w')

p = Pair()
p.newPair(argv[1],"source-document02634.txt")


