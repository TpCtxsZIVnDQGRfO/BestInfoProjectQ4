import numpy as np
import numba

#Hallo und herzlich willkommen in der Welt der Performanceoptimierung
#Da die wunderbare Library Numpy sich entschieden hat keine sinnvolle Funktion
#das shiften von Arrays zu verfügung zu stellen, musste ich das machen :)
#die Lösung ist inspiriert durch einen Stackoverflow-Eintrag
#url: https://stackoverflow.com/questions/30399534/shift-elements-in-a-numpy-array
#und meines wissens outperformt alle anderen Lösuungen auf großen Arrays(75000 Einträge)
#Anmerkung froll steht für fast roll(die analoge (schlechte) numpy Funktion)
def froll(arr, shift, fill_value = 0):
    #1D shift, arr, shift (wenn positiv nach rechts), fill_value: damit werden leere Einträge aufgefüllt
    if num >0:
        arr[shift:] = arr[:-shift]
        arr[:shift] = fill_value
    if num <0:
        arr[:shift] = arr[-num:]
        arr[shift:] = fill_value
    return arr

def froll2d(arr, shift, fill_value = 0):
    if shift[0]>0:
        arr[shift[0]:,:] = arr[:-shift[0],:]
        arr[:shift[0],:] = fill_value
    if shift[0]<0:
        arr[:shift[0],:] = arr[-shift[0]:,:]
        arr[shift[0]:,:] = fill_value
    if shift[1]>0:
        arr[:,shift[1]:] = arr[:,:-shift[1]]
        arr[:,:shift[1]] = fill_value
    if shift[1]<0:
        arr[:,:shift[1]] = arr[:,-shift[1]:]
        arr[:,shift[1]:] = fill_value
    return arr

##test = np.array([[1,2,3],[4,5,6],[7,8,9]])
##print(test)
##print(froll2d(test,[-1,-1]))
