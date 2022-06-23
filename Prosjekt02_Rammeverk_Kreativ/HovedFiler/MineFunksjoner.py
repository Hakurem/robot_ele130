def EulerForward(g,f,Ts,k):
	res = g[k-1] + f[k-1]*Ts[k-1]
	g.append(res)
	

def FirFilter():
	pass

def IIRFilter():
	pass

def Num_Derivasjon():
	pass

def CalculatePowers():
	pass


def calculatePower(d,k):
	if  d.W_[k]: 
		d.PowerA.append(50)
	else:
		d.PowerA.append(0)

	if  d.A_[k]: 
		d.PowerB.append(50)
	else:
		d.PowerB.append(0)

	if  d.S_[k]: 
		d.PowerC.append(50)
	else:
		d.PowerC.append(0)

	if  d.D_[k]: 
		d.PowerD.append(50)
	else:
		d.PowerD.append(0)
