
# scale 10 is 1cycle=1ns
SCALE = 10
HBYTE = 30
UNIT=16
FMHz = 100.0*SCALE
nsPerCycle = 1
# measure bw
READMPS = 512
MPS = 512
#fixed don't change
RCTLP_SIZE = 256

#approx. mem read delay
ReadDelay = 90

BW = 16
LinkDelay = 1 #int(15.0/(BW*nsPerCycle))
DelayCycle = 405
#512//16 = 32
# Credit = 320 #int((11.5*nsPerCycle*LinkDelay/(64*SCALE))*2)
Credit = 15 #int((11.5*nsPerCycle*LinkDelay/(64*SCALE))*2)

# this is very necessary and don't touch
AdditionalCost = 1
ProcessTLPCost = 7
