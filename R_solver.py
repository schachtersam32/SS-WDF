#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  1 10:30:45 2021

@author: samschachter
"""

import scipy
import numpy as np
from sympy import Matrix,diag,zeros,eye,simplify
from sympy.solvers import solve, solve_linear
from sympy.abc import symbols
from sympy.interactive.printing import init_printing
init_printing(use_unicode=False, wrap_line=False)        

class Resistor:
    
    def __init__(self, name, n1, n2, value,is_val_symbolic):
        self.name = name
        self.n1 = n1
        self.n2 = n2
        self.r_value = value
        self.g_value = 1/value
        self.is_val_symbolic = is_val_symbolic
        
        self.info = [name,n1,n2,value,self.g_value,is_val_symbolic]
        
    def addToMNA(self,Y):
        Y[self.n1-1,self.n1-1] += self.g_value
        Y[self.n1-1,self.n2-1] += -self.g_value
        Y[self.n2-1,self.n1-1] += -self.g_value
        Y[self.n2-1,self.n2-1] += self.g_value
        
        return Y
        
def parse_netlist_resistor(line):
    vals = line.split()
    
    Name = symbols(vals[0])
    N1 = int(vals[1].replace('N',''))
    N2 = int(vals[2].replace('N',''))
    if vals[3].isalpha() == False:
        R_val = float(vals[3]) # add code to differentiate between string and float
        is_sym = False
    else:
        R_val = symbols(vals[3])
        is_sym = True
    
    res = Resistor(Name,N1,N2,R_val,is_sym)

    return res
        
class VoltageSource:
    
    def __init__(self,name,n1,n2):
        self.name = name
        self.n1 = n1
        self.n2 = n2
        
        self.info = [name,n1,n2]
        
    def addToMNA(self,A1,i):
        A1[self.n1-1,i] = 1
        A1[self.n2-1,i] = -1
        
        return A1
        
def parse_netlist_vsource(line):
    vals = line.split()
    
    Name = symbols(vals[0])
    N1 = int(vals[1].replace('N',''))
    N2 = int(vals[2].replace('N',''))
    
    vol = VoltageSource(Name,N1,N2)

    return vol
    
class TwoPort:
    
    def __init__ (self,name,n1,n2,sn1,sn2,value,model_type,in_impedance=3000000,out_impedance=75):
        self.name = name
        self.n1 = n1
        self.n2 = n2
        self.sn1 = sn1
        self.sn2 = sn2
        self.value = value
        self.model_type = model_type
        self.in_impedance = in_impedance
        self.out_impedance = out_impedance
        
        self.info = [name,n1,n2,sn1,sn2,value,model_type]        
        
    def addNullor(self,B2,A2):
        B2[self.sn1-1] = 1
        B2[self.sn2-1] = -1
        A2[self.n1-1] = 1
        A2[self.n2-1]= -1
        
        return B2, A2
        
    def addIdealVCVS(self,B2,A2):
        B2[self.sn1-1] = -self.value
        B2[self.sn2-1] = self.value
        B2[self.n1-1] = 1
        B2[self.n2-1]= -1
        
        A2[self.n1-1] = 1
        A2[self.n2-1] = -1
        
        return B2,A2
        
    def addResistiveVCVS(self,Y,B2,A2,D22,i):
        
        Y[self.sn1-1,self.sn1-1] += 1./self.in_impedance
        Y[self.sn1-1,self.sn2-1] += -1./self.in_impedance
        Y[self.sn2-1,self.sn1-1] += -1./self.in_impedance
        Y[self.sn2-1,self.sn2-1] += 1./self.in_impedance
        
        B2[self.sn1-1] = -self.value
        B2[self.sn2-1] = self.value
        B2[self.n1-1] = 1
        B2[self.n2-1]= -1
        
        A2[self.n1-1] = 1
        A2[self.n2-1] = -1
        
        D22[i,i] = self.out_impedance
        
        return Y,B2,A2,D22
    
    def addToMNA(self,Y,B2,A2,D22,i):
        if(model_type == 0):
            B2,A2 = self.addNullor(B2,A2)
        elif(model_type == 1):
            B2,A2 = self.addIdealVCVS(B2,A2)
        elif(model_type == 2):
            Y,B2,A2,D22 = self.addResistiveVCVS(Y,B2,A2,D22,i)
            
        return Y,B2,A2,D22

def parse_netlist_twoport(line,model_type):
    vals = line.split()
    
    Name = symbols(vals[0])
    N1 = int(vals[1].replace('N',''))
    N2 = int(vals[2].replace('N',''))
    Sn1 = int(vals[3].replace('N',''))
    Sn2 = int(vals[4].replace('N',''))
    value = int(vals[5])

    tp = TwoPort(Name,N1,N2,Sn1,Sn2,value,model_type)

    return tp


###### SCRIPT START ###### 
    
file1 = "Netlists/MXR_Dist_VCVS_thev.net"
file2 = "Netlists/Bassman_Thev_ports.net"

### OPTIONS ###
model_type = 2 #0 = nullor, 1 = ideal vcvs, 2 = resistive vcvs
datum_node = 1
adapt_port = True
port_to_adapt = 0

# read values from netlist
with open (file1 ,"r") as my_file:
    netlist = my_file.readlines()
    print(netlist)
    
netlist.pop()
netlist.pop()
netlist.pop(0)

nLines = len(netlist)

elements = []
resistors = []
vsources = []
twoports = []
numPorts = 0
numEtc = 0

for idx,line in enumerate(netlist):
    if line[0] == 'R':
        res = parse_netlist_resistor(line)
        elements.append(res)
        resistors.append(res)
        print(res.info)
    elif line[0] == 'V':
        vol = parse_netlist_vsource(line)
        elements.append(vol)
        vsources.append(vol)
        numPorts += 1
        print(vol.info)
    elif line[0] == 'E':
        tp = parse_netlist_twoport(line,model_type)
        elements.append(tp)
        twoports.append(tp)
        numEtc += 1
        print(tp.info)
        
numNodes = max([e.n1 for e in elements] + [e.n2 for e in elements])
    
# allocate MNA matrices
Y = zeros(numNodes,numNodes)
A1 = zeros(numNodes,numPorts)
A2 = zeros(numNodes,numEtc)
B2 = zeros(numEtc,numNodes)
D11 = zeros(numPorts,numPorts)
D12 = zeros(numPorts,numEtc)
D21 = zeros(numEtc,numPorts)
D22 = zeros(numEtc,numEtc)
Rp = Matrix(numPorts,numPorts,lambda i,j: resistors[i].r_value if i == j else 0)

## Time to fill in matrices ##

for r in resistors:
    Y = r.addToMNA(Y)
    
for i,v in enumerate(vsources):
    A1 = v.addToMNA(A1,i)
    
if numEtc > 0:
    for i,t in enumerate(twoports):
        Y,B2,A2,D22 = t.addToMNA(Y,B2,A2,D22,i)
        
B1 = A1.T;
#X = zeros(numPorts+numNodes+numEtc,numPorts+numNodes+numEtc)
# annoying, but manually add values to X
# BlockMatrix([[Y,A1,A2],[B1,D11,D12],[B2,D21,D22]])
Y_temp = Y.row_join(A1.row_join(A2))
B1_temp = B1.row_join(D11.row_join(D12))
B2_temp = B2.row_join(D21.row_join(D22))
X = Y_temp.col_join(B1_temp.col_join(B2_temp))

X.row_del(datum_node-1)
X.col_del(datum_node-1)

numNodes = numNodes - 1

### finally calculate S matrix ###
I = eye(numPorts)
Z1 = zeros(numPorts,numNodes)
Z2 = zeros(numPorts,numEtc)
ZIZ = Z1.row_join(I.row_join(Z2))

S = I + 2*Rp*ZIZ*X**-1*ZIZ.T

### adapt port if so desired ##
#if adapt_port == True:
#    adaptedPort = Rp[port_to_adapt,port_to_adapt]
#    adaptedEntry = simplify(S[port_to_adapt,port_to_adapt])
#    s_adapted = solve_linear(adaptedPort,adaptedEntry)
#    for i,s in enumerate(S):
#        S[i] = s.subs(s_adapted[0],s_adapted[1])

with open('SMatrix.txt',mode='w') as outFile:
    for i in range(numPorts):
        for j in range(numPorts):
            print('S[',i,'][',j,'] = ',simplify(S[i,j]),file=outFile)
