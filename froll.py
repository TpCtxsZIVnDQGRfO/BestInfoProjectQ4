import numpy as np

#Hallo und herzlich willkommen in der Welt der Performanceoptimierung
#Da die wunderbare Library Numpy sich entschieden hat keine sinnvolle Funktion
#das shiften von Arrays zu verfügung zu stellen, musste ich das machen :)
#die Lösung ist inspiriert durch einen Stackoverflow-Eintrag
#url: https://stackoverflow.com/questions/30399534/shift-elements-in-a-numpy-array
#und meines wissens outperformt alle anderen Lösuungen auf großen Arrays(75000 Einträge)
#Anmerkung froll steht für fast roll(die analoge (schlechte) numpy Funktion)

#destructive fast roll
#Diese Methode ist einwenig schneller aus größeren arrays ,da sie die Einträge ändert und nicht ein neues Array zuweist
def dfroll(arr, shift, fill_value = 0):
    #1D shift, arr, shift (wenn positiv nach rechts), fill_value: damit werden leere Einträge aufgefüllt
    temp = np.zeros(arr.shape)
    if shift >0:
        temp[shift:] = arr[:-shift]
        temp[:shift] = arr
    if shift <0:
        temp[:shift] = arr[-shift:]
        temp[shift:] = arr
    return temp
#destructive fast roll 2 dimensional
#analog zu dfroll
def dfroll2d(arr, shift, fill_value = 0):
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
# dfroll2d mit Zuweisung eines neuen arrays
def froll2d(arr, shift, fill_value = 0):
    temp = np.zeros(arr.shape)
    if shift[0] == 0:
        temp = np.copy(arr)
    if shift[0]>0:
        temp[shift[0]:,:] = arr[:-shift[0],:]
        temp[:shift[0],:] = fill_value
    if shift[0]<0:
        temp[:shift[0],:] = arr[-shift[0]:,:]
        temp[shift[0]:,:] = fill_value
    if shift[1]>0:
        temp[:,shift[1]:] = temp[:,:-shift[1]]
        temp[:,:shift[1]] = fill_value
    if shift[1]<0:
        temp[:,:shift[1]] = temp[:,-shift[1]:]
        temp[:,shift[1]:] = fill_value
    return temp
#Gubt das geschiftete Array wieder, Eintrage die am einen Ende "rausgeschoben" werden tauchen an anderen wieder auf
def froll2d2(arr, shift):
    temp = np.zeros(arr.shape)
    if shift[0] == 0:
        temp = np.copy(arr)
    if shift[0]>0:
        temp[:shift[0],:] = arr[-shift[0]:,:]
        temp[shift[0]:,:] = arr[:-shift[0],:]
    if shift[0]<0:
        temp[shift[0]:,:] = arr[:-shift[0],:]
        temp[:shift[0],:] = arr[-shift[0]:,:]
    if shift[1]>0:
        temp[:,:shift[1]] = temp[:,-shift[1]:]
        temp[:,shift[1]:] = temp[:,:-shift[1]]
    if shift[1]<0:
        temp[:,shift[1]:] = temp[:,shift[1]:]
        temp[:,:shift[1]] = temp[:,-shift[1]:]
    return temp


##test = np.array([[1,2,3],[4,5,6],[7,8,9]])
##print(test)
##print(froll2d(test,[-1,-1]))
