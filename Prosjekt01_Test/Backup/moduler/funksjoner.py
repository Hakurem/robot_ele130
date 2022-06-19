# Bunch klassen arver fra dictionary og gir støtte til punktum-notasjon
# Fordi vi bruker punktum-notasjon er det ikke eksplisitt 
# at det vi kaller på er en funksjon/metode eller en egendefinert-variabel
# OBS! unngå å navngi listene dine med innebygde metoder fra dictionary

# minimalt støtte til punktumnotasjon i micropython
class Bunch(dict):
    def __init__(self, *args, **kwds):
        super(Bunch, self).__init__(*args, **kwds)
        self.__dict__.update(self)


# Støttes i python 3, men ikke i micropython. Mye mer funksjonalitet
class BunchPython(dict):
    def __init__(self, *args, **kwds):
        super(BunchPython, self).__init__(*args, **kwds)
        self.__dict__ = self



# Konverterer tekst-variabler, 
# henter ut verdier, formaterer til en streng og returnerer
def EasyWrite(d,k,*variabelNavn):
    streng = ""    
    last_index = len(variabelNavn)-1
    if k == 0:
		# Skriv variabelnavn på første linje
        for i,v in enumerate(variabelNavn):
            if i == last_index:
                streng += "{navn}\n".format(navn = v)
            else:
                streng += "{navn}, ".format(navn = v)
        # lager et mellomrom
        streng  += "\n"

    # Så skriver vi bare verdiene som strenger


    for i,v in enumerate(variabelNavn):
        if i == last_index:
            try:
                streng += str(d.__dict__[v][-1])
            except IndexError:
                pass
        else:
            try:
                streng += str(d.__dict__[v][-1]) + ","
            except IndexError:
                streng += ","
    streng  += "\n"
    return streng
#_________________________________________________________



# Pakker sammen live målinger for plotting
def packLiveData(d,*variabelNavn):
    LiveData = {}
    for key in variabelNavn:
        if key in d.__dict__:
            try:
                LiveData[key] = d.__dict__[key][-1]
            except IndexError:
                pass
        else:
            raise Exception("Du la inn et variabelnavn som ikke finnes. Sjekk at du har stavet korrekt")
    return LiveData

# Pakker opp målinger fra til plotting
def unpackLiveData(d,LiveData):
    for key in LiveData:
        if key in d:
            d[key].append(LiveData[key])
        else:
            # Skal i prinsippet aldri skje
            raise Exception("Keys does not match when unpacking live data")
#_____________________________________


# Finner ut om streng-verdien er en int eller float
# om det ikke er noen av delene returnerer den strengen tilbake
def parseMeasurements(s):
    try:
        return int(s)
    except ValueError:
        pass
    try:
        return float(s)
    except ValueError:
        pass
    return s
	
    
# Pakker opp data i offline modus fra filenameMeasurement
def unpackMeasurement(d,keys,measures):
	for i,key in enumerate(keys):
		if key in d:
			d[key].append(parseMeasurements(measures[i]))
#___________________________________________________________








