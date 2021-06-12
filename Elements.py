#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 12 16:28:17 2021

@author: samschachter
"""
from sympy.abc import symbols
from sympy import Matrix,zeros,eye,simplify

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
        if(self.model_type == 0):
            B2,A2 = self.addNullor(B2,A2)
        elif(self.model_type == 1):
            B2,A2 = self.addIdealVCVS(B2,A2)
        elif(self.model_type == 2):
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

