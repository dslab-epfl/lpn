from lpnlang import Token
from collections import deque
from .all_enum import CstStr
from .places import *

def collect_dependency(file):
   with open(file, "r") as f:
      lines = f.readlines()
      for line in lines:
         line = line.strip().split(",")
         c1, c2, c3, c4 = int(line[0]), int(line[1]),int(line[2]),int(line[3]) 
         sum_c = sum([c1, c2, c3, c4])
         if sum_c != 0 :
            print("should exit")
            # exit()
         return c1, c2, c3, c4
   
   return 0, 0, 0, 0

def toEnum(val):
   if val == "load":
      return CstStr.LOAD
   elif val == "compute":
      return CstStr.COMPUTE
   elif val == "store":
      return CstStr.STORE
   elif val == "sync":
      return CstStr.SYNC
   elif val == "finish":
      return CstStr.FINISH
   elif val == "alu":
      return CstStr.ALU
   elif val == "loadAcc":
      return CstStr.LOADACC
   elif val == "loadUop":
      return CstStr.LOADUOP
   elif val == "gemm":
      return CstStr.GEMM
   elif val == "inp":
      return CstStr.INP
   elif val == "wgt":
      return CstStr.WGT
   elif val == "empty":
      return CstStr.EMPTY
   else:
      print(val, " is not in my dictionary")
      assert(0)

def collect_insns(file):
   tokens = deque()
   cnt = 0
   with open(file, "r") as f:
      lines = f.readlines()
      for line in lines:
         cnt += 1
         line = line.replace(" ", "")
         line = line.strip().split(",")
         tokens.append(Token(dict({
         "opcode": toEnum(line[1]),
         "subopcode": toEnum(line[2]),
         "tstype": toEnum(line[3]),
         "xsize": int(line[4]), 
         "ysize": int(line[5]), 
         "uop_begin": int(line[6]), 
         "uop_end": int(line[7]), 
         "lp_1": int(line[8]), 
         "lp_0": int(line[9]), 
         "use_alu_imm": int(line[10]), 
         "pop_prev":int(line[11]), 
         "pop_next":int(line[12]), 
         "push_prev":int(line[13]), 
         "push_next":int(line[14]) })))
   
   print("insn length ", cnt)
   return tokens
    
