import numpy as np
import matplotlib.pyplot as plt
import math
from froll import froll2d
from numba import jit
#Allgemeine Simulationsklasse für das Informatikprojekt
#LK Winkler 2021 Q4 KKOS

#Grundlegende Struktur:
#Eine Simulation wird als 4D Array aufgefasst mit:
#1 Zustandsdimension (Zustände)
#2 Raumdimensionen   (Board)
#1 Zeitdimension     (Zeit)

#Zwischen den verschiedenen Zuständen lässt sich mithilfe einer Flow-Matrix
#die Richtung und der Typ(jeder Typ erhält einen eindeutiger int Wert) des Flusses beschreiben
#Die Typen werden in einem Nachbarschaftarray gespeichert und bestehen wiederum
#aus 2D Arrays, welche eine Wahrscheinlichkeit zur Übertragung ausgehend vom
#Mittelpunkt des Arrays beinhalten

#Zur Initialisierung erhält die Klasse, den Startzustand des Boards (Board[0]),
#die Vollständige Flowmatrix(0 reserviert als kein Fluss), das FLowchart, besteht aus der Übertragungswahrscheinlichkeit und dem Träger

class simulation:
    def __init__(self, starting_conditions,iterations, flow_matrix, flow_chart):
        self.iter = iterations 
        #Initialisierung des Arrays zur Speicherung der Simulation:
        self.images = np.zeros([iterations,starting_conditions.shape[0],starting_conditions.shape[1],starting_conditions.shape[2]])
        self.images[0] = starting_conditions

        #Initialisierung der verschiedenen Übertragungen
        for i in range(len(flow_chart)):
            if len(flow_chart[i][0].shape)>1:
                midpoint = [(flow_chart[i][0].shape[0]-1)/2,(flow_chart[i][0].shape[1]-1)/2]
                non_zero = np.nonzero(flow_chart[i][0])
                temp = np.array([non_zero[0],non_zero[1],flow_chart[i][0][non_zero]])
                temp[0] = temp[0] - midpoint[0]
                temp[1] = temp[1] - midpoint[1]
            if len(flow_chart[i][0].shape) == 1:
                temp = np.array([[0],[0],[flow_chart[i][0][0]]])
            #Aus dem Nachbarschaftsarray werden alle non zero Einträge ausgelesen und in ein
            #Array umgewandelt, welches die Koordinaten, sowie den Eintrag speichert
            flow_chart[i][0] = temp
        self.flow = []
        for i in range(flow_matrix.shape[0]):
            for j in range(flow_matrix.shape[1]):
                if flow_matrix[i,j] != 0:
                    self.flow.append(flow_chart[flow_matrix[i,j]-1])
                    self.flow[-1].append([i,j])
    def spread(self,board, candidates, n):
        #Parameter: board: Zellen, die Verbreiten können, canidates: Zellen, die "angesteckt" werden können, n: liste der Nachbarschafts
        random = np.random.rand(board.shape[0],board.shape[1])
        new = np.zeros([board.shape[0],board.shape[1]])
        for i in range(len(n[0])):
            temp = froll2d((random+n[2][i])*board,[int(n[0][i]),int(n[1][i])])
            temp = temp.astype(int)
            new = (new + temp).astype(bool)
        return new*candidates
    def run(self):
        for i in range(1, self.iter, 1):
            self.images[i] = self.images[i-1]
            for j in range(len(self.flow)):
                temp = self.spread(self.images[i-1,:,:,self.flow[j][1]], self.images[i-1,:,:,self.flow[j][2][0]],self.flow[j][0])
                self.images[i,:,:,self.flow[j][2][0]] = self.images[i,:,:,self.flow[j][2][0]] - temp
                self.images[i,:,:,self.flow[j][2][1]] = self.images[i,:,:,self.flow[j][2][1]] + temp
    def get(self,t):
        #Gibt das Board zum Zeitpunkt t zurück. Ist t größer als die Anzahl der Iteration gibt das letzte Element aus.
        #Ist t kleiner 0 gibt das t=0 aus.
        if t>self.iter-1:
           return self.images[-1]
        elif t<0:
            return self.images[0]
        else:
            return self.images[t]
    def generate_graph(self):
        #Gibt die Anzahl der Zellen in den jeweiligen Zuständen in abhängigkeit zur Zeit an,
        #gibt ein 2d Numpy Array an, erste Dimension alle Zusände, 2. Dimension Zeitkomponente
        graph = np.sum(self.images,(1,2))
        x = np.arange(0, self.iter)
        #eigene Ausgabe der Graphen
        #plt.stackplot(x,graph.transpose())
        #plt.show()
        return graph.transpose()
#------------------------------------------------Beispielinitialisierung SIR-Modell:------------------------------------------------------
#Ein beispielhafte Anwendung wäre das SIR-Modell (mit räumlicher Beschränkung) soll stark vereinfacht die Verbreitung von Krankenheiten
#in  einer festen Bevölkerung modellieren, Jede Zelle steht für eine Person und hat zu jedem Zeitpunkt t eine der folgenden Eigenschaften:
#Hierbei gibt es 3 Zustände:
#1: Suscepteble (infizierbar)
#2: Infective   (infiziert)
#3: Recoverd    (immun)
#Der Fluss hat die From S-(I)->I-(I)->R
#Wobei -(I)->, dafür steht, dass die Infektion von infizierten Zellen ausgelöst wird, bzw. die Erholung auch bei infizierten Zellenabläuft
#Und läuft wie folgt ab:
#Eine infizierte Zelle kann anliegende Zellen infizieren
#Eine Zelle wird immun mit einer gewissen Wahrscheinlichkeit
flow_m = np.array([[0,1,0],[0,0,2],[0,0,0]])#Flow-Matrix
infection = np.array([[1,1,1],[1,0,1],[1,1,1]])*0.3#Nachbarschaft für die Infektion
recovery = np.array([0.6])#Nachabrschaft für die Erholung
flow_c = [[infection,1],[recovery,1]]#Flow-Chart

start = np.zeros([200,200,3])#Festlegung der Größe des Boards
start[:,:] = [1,0,0]# Festlegung der Susceptebles 
start[50:55,50:55] = [0,1,0]#Festlegung der anfänglichen Infizierten
start[100:105,100:105] = [0,1,0]
sir = simulation(start, 300, flow_m, flow_c)
sir.run()
##for i in range(0,700,50):
##    plt.imshow(sir.get(i))
##    plt.show()
sir.generate_graph()
#------------------------------------------------------------------------------------------------------------------------------------------

