from Model.Document import *
from Model.Pair import *

import io
import sys

print("Running Driver 2")
sys.stdout = open('Log/Log-Driver2.txt', 'w')

p = Pair()
#suspicious-document01379.txt source-document00834.txt
#p = Pair("suspicious-document00111.txt","source-document02907.txt")
#p.newPair("suspicious-document00460.txt","source-document03174.txt") #No Obs

#p.newPair("suspicious-document00001.txt","source-document00294.txt")

#p.newPair("suspicious-document00017.txt","source-document00189.txt") #NO PLAG
#p.newPair("suspicious-document00017.txt","source-document00876.txt") #NO PLAG
#p = Pair("suspicious-document00056.txt","source-document02801.txt") #NO PLAG
print("LOAD PAIR")

p.newPair("suspicious-document00849.txt","source-document01077.txt") #Random
#p = Pair("suspicious-document00027.txt","source-document02493.txt") #Random

#p.newPair("suspicious-document00460.txt","source-document03174.txt") #Summary

#p.newPair("suspicious-document01102.txt","source-document00480.txt")
#p.newPair("suspicious-document01400.txt","source-document01611.txt")
#p.newPair("suspicious-document01412.txt","source-document00716.txt")
print("Size Susp")
print(len(p.src.text))
print("Size Src")
print(len(p.susp.text))

print("PR")
print(p.pr)
print("Perfomansi")
print(p.perf)
print("F1")
print(p.f1)
print("S")
print(p.s)
print("R")
print(p.r)

for item in p.r:
	print(p.src.text[item[0]:item[1]])
	print("\n")
	print(p.susp.text[item[2]:item[3]])
	print("------")

print(p.perf)
print(p.f1)
print(p.rperf)
print(p.rf1)
print(p.norm)
print(p.normf1)