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
# konverterer dataobjektet bunch til denne typen når vi detekterer at vi er på PC
class BunchPython(dict):
    def __init__(self, *args, **kwds):
        super(BunchPython, self).__init__(*args, **kwds)
        self.__dict__ = self


# Konverterer tekst-variabler, 
# henter ut verdier, formaterer til en streng og returnerer
keyOrder = [] # iterering i dictionary garanterer oss ikke samme rekkefølge (vi lager rekkefølgen selv)
def writeToFile(d,k,meas,_g):
    
    
    d_map = d.__dict__
    if k == 0:
        for key in d_map:
            keyOrder.append(key)
    last_index = len(keyOrder)-1
    streng = ""
    if k == 0:
        # Skriv variabelnavn på første linje og marker om dette er en måling eller beregning 
        g_map = _g.__dict__
        for i,v in enumerate(keyOrder):
            if v in meas:
                if i == last_index:
                    streng += "{navn}=meas\n".format(navn=v)
                else:
                    streng += "{navn}=meas,".format(navn=v)
            else:
                if i == last_index:
                    streng += "{navn}=calc\n".format(navn=v)
                else:
                    streng += "{navn}=calc,".format(navn=v)

        # lagring av initialverdier som brukes i mathcalculations
        for i,v in enumerate(g_map):
            value = g_map[v]
            if i == len(g_map)-1:
                streng += "{navn}={value}\n".format(navn=v, value=value)
            else:
                streng += "{navn}={value},".format(navn=v, value=value)
      
    # Så skriver vi bare verdiene som strenger
    for i,v in enumerate(keyOrder):
        if i == last_index:
            try:
                value = d_map[v][-1]
                streng += str(value)
            except IndexError:
                pass
        else:
            try:
                value = d_map[v][-1]
                streng += str(value) + ","
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
    return s.strip()
	
    
# Pakker opp data i offline modus fra filenameMeasurement
def unpackMeasurement(d,keys,m_keys,Data):
    for i,key in enumerate(keys):
        if key in keys and key in m_keys:
            d[key].append(parseMeasurements(Data[i]))
            
#___________________________________________________________








