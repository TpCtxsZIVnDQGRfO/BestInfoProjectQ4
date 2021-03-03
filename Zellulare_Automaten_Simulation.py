import numpy as np
import matplotlib.pyplot as plt
import math
from froll import dfroll2d
from froll import froll2d


# Allgemeine Simulationsklasse für das Informatikprojekt
# LK Winkler 2021 Q4 KKOS

# Grundlegende Struktur:
# Eine Simulation wird als 4D Array aufgefasst mit:
# 1 Zustandsdimension (Zustände)
# 2 Raumdimensionen   (Board)
# 1 Zeitdimension     (Zeit)

# Zwischen den verschiedenen Zuständen lässt sich mithilfe einer Flow-Matrix
# die Richtung und der Typ(jeder Typ erhält einen eindeutiger int Wert) des Flusses beschreiben
# Die Typen werden in einem Nachbarschaftarray gespeichert und bestehen wiederum
# aus 2D Arrays, welche eine Wahrscheinlichkeit zur Übertragung ausgehend vom
# Mittelpunkt des Arrays beinhalten

# Zur Initialisierung erhält die Klasse, den Startzustand des Boards (Board[0]),
# die Vollständige Flowmatrix(0 reserviert als kein Fluss), das FLowchart, besteht aus der Übertragungswahrscheinlichkeit und dem Träger

class simulation:
    def __init__(self, starting_conditions, iterations, flow_matrix, flow_chart):
        self.iter = iterations
        # Initialisierung des Arrays zur Speicherung der Simulation:
        self.data = np.zeros(
            [iterations, starting_conditions.shape[0], starting_conditions.shape[1], starting_conditions.shape[2]])
        self.data[0] = starting_conditions
        self.images = "Images not yet generated"

        # Initialisierung der verschiedenen Übertragungen
        for i in range(len(flow_chart)):
            if len(flow_chart[i][0].shape) > 1:
                midpoint = [(flow_chart[i][0].shape[0] - 1) / 2, (flow_chart[i][0].shape[1] - 1) / 2]
                non_zero = np.nonzero(flow_chart[i][0])
                temp = np.array([non_zero[0], non_zero[1], flow_chart[i][0][non_zero]])
                temp[0] = temp[0] - midpoint[0]
                temp[1] = temp[1] - midpoint[1]
            if len(flow_chart[i][0].shape) == 1:
                temp = np.array([[0], [0], [flow_chart[i][0][0]]])
            # Aus dem Nachbarschaftsarray werden alle non zero Einträge ausgelesen und in ein
            # Array umgewandelt, welches die Koordinaten, sowie den Eintrag speichert
            flow_chart[i][0] = temp
        self.flow = []
        for i in range(flow_matrix.shape[0]):
            for j in range(flow_matrix.shape[1]):
                if flow_matrix[i, j] != 0:
                    self.flow.append(flow_chart[flow_matrix[i, j] - 1])
                    self.flow[-1].append([i, j])

    def spread(self, board, candidates, n):
        # Parameter: board: Zellen, die Verbreiten können, canidates: Zellen, die "angesteckt" werden können, n: liste der Nachbarschafts
        random = np.random.rand(board.shape[0], board.shape[1])
        new = np.zeros([board.shape[0], board.shape[1]])
        for i in range(len(n[0])):
            temp = dfroll2d((random + n[2][i]) * board, [int(n[0][i]), int(n[1][i])])
            temp = temp.astype(int)
            new = (new + temp).astype(bool)
        return new * candidates

    def run(self):
        for i in range(1, self.iter, 1):
            self.data[i] = self.data[i - 1]
            for j in range(len(self.flow)):
                temp = self.spread(self.data[i - 1, :, :, self.flow[j][1]], self.data[i - 1, :, :, self.flow[j][2][0]],
                                   self.flow[j][0])
                self.data[i, :, :, self.flow[j][2][0]] = self.data[i, :, :, self.flow[j][2][0]] - temp
                self.data[i, :, :, self.flow[j][2][1]] = self.data[i, :, :, self.flow[j][2][1]] + temp

    def get_data(self, t):
        # Gibt das Board zum Zeitpunkt t zurück. Ist t größer als die Anzahl der Iteration gibt das letzte Element aus.
        # Ist t kleiner 0 gibt das t=0 aus.
        if t > self.iter - 1:
            return self.data[-1]
        elif t < 0:
            return self.data[0]
        else:
            return self.data[t]

    def get_image(self, t):
        # Gibt das Bild zum Zeitpunkt t zurück
        # Analog zu get_data
        if t > self.iter - 1:
            return self.images[-1]
        elif t < 0:
            return self.images[0]
        else:
            return self.images[t]

    def generate_graph(self):
        # Gibt die Anzahl der Zellen in den jeweiligen Zuständen in abhängigkeit zur Zeit an,
        # gibt ein 2d Numpy Array an, erste Dimension alle Zusände, 2. Dimension Zeitkomponente
        graph = np.sum(self.data, (1, 2))
        # x = np.arange(0, self.iter)
        # eigene Ausgabe der Graphen
        ##        plt.stackplot(x,graph.transpose())
        ##        plt.show()
        return graph.transpose()

    def generate_images(self):
        self.images = np.zeros(list(self.data.shape[:3]) + [3])
        colors = np.zeros([self.data.shape[3], 3])
        for i in range(self.data.shape[3]):
            colors[i][0] = i * 1 / self.data.shape[3]
            colors[i][1] = 1 - i * 1 / self.data.shape[3]
            colors[i][2] = 1 - i * 1 / self.data.shape[3]
        for i in range(self.data.shape[3]):
            self.images[self.data[:, :, :, i] == 1] = colors[i]


class oneD_cellular_automata:
    # Mir wurde von einem Mitschüler gesagt, dass man keine Zellulären Autimaten ohne Conways Game of Life macht,
    def __init__(self, iterations, rules, start):
        self.iterations = iterations
        self.rules = rules
        self.start = start
        self.data = np.zeros([iterations, start.shape[0]])
        self.data[0] = start

    # StateFunktion, definiton für alle Möglichkeiten
    def f(self, y, x, z):
        if x == 0 and y == 0 and z == 0:
            return self.rules[0]
        if x == 0 and y == 0 and z == 1:
            return self.rules[1]
        if x == 0 and y == 1 and z == 0:
            return self.rules[2]
        if x == 0 and y == 1 and z == 1:
            return self.rules[3]
        if x == 1 and y == 0 and z == 0:
            return self.rules[4]
        if x == 1 and y == 0 and z == 1:
            return self.rules[5]
        if x == 1 and y == 1 and z == 0:
            return self.rules[6]
        else:
            return self.rules[7]

    def run(self):
        for i in range(1, self.iterations, 1):
            for j in range(1, self.data.shape[0] - 1, 1):
                self.data[i][j] = self.f(self.data[i - 1][j - 1], self.data[i - 1][j], self.data[i - 1][j + 1])


class conways_game_of_life:
    def __init__(self, start, iterations):
        self.iterations = iterations
        self.data = np.zeros([iterations, start.shape[0], start.shape[1]])
        self.data[0] = start

    def rules(self, array):
        convolution = np.zeros(array.shape)
        for i in range(-1, 2, 1):
            for j in range(-1, 2, 1):
                print([i, j])
                # plt.imshow(array+ froll2d(array, [i, j]))
                # plt.show()
                convolution = convolution + froll2d(array, [i, j])
        convolution = convolution - array
        # plt.imshow(convolution)
        # plt.show()
        array[convolution < 2] = 0
        array[convolution > 3] = 0
        array[convolution == 3] = 1
        return array

    def run(self):
        for i in range(1, self.iterations, 1):
            self.data[i] = self.rules(np.copy(self.data[i - 1]))


# ------------------------------------------------Beispielinitialisierung SIR-Modell:------------------------------------------------------
# Ein beispielhafte Anwendung wäre das SIR-Modell (mit räumlicher Beschränkung) soll stark vereinfacht die Verbreitung von Krankenheiten
# in  einer festen Bevölkerung modellieren, Jede Zelle steht für eine Person und hat zu jedem Zeitpunkt t eine der folgenden Eigenschaften:
# Hierbei gibt es 3 Zustände:
# 1: Suscepteble (infizierbar)
# 2: Infective   (infiziert)
# 3: Recoverd    (immun)
# Der Fluss hat die From S-(I)->I-(I)->R
# Wobei -(I)->, dafür steht, dass die Infektion von infizierten Zellen ausgelöst wird, bzw. die Erholung auch bei infizierten Zellenabläuft
# Und läuft wie folgt ab:
# Eine infizierte Zelle kann anliegende Zellen infizieren
# Eine Zelle wird immun mit einer gewissen Wahrscheinlichkeit
# flow_m = np.array([[0,1,0],[0,0,2],[0,0,0]])#Flow-Matrix
# infection = np.array([[1,1,1],[1,0,1],[1,1,1]])*0.3#Nachbarschaft für die Infektion
# recovery = np.array([0.6])#Nachabrschaft für die Erholung
# flow_c = [[infection,1],[recovery,1]]#Flow-Chart
#
# start = np.zeros([200,200,3])#Festlegung der Größe des Boards
# start[:,:] = [1,0,0]# Festlegung der Susceptibles
# start[50:55,50:55] = [0,1,0]#Festlegung der anfänglichen Infizierten
# start[100:105,100:105] = [0,1,0]
# sir = simulation(start, 300, flow_m, flow_c)
# sir.run()
# sir.generate_images()
# for i in range(0,300,50):
#     plt.imshow(sir.images[i])
#     plt.show()
# sir.generate_graph()
# ------------------------------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------Beispiel Initialisierung 2------------------------------------------------------------------
# flow_m = np.array([[0,1,0,0],[0,0,0,2],[0,3,0,0],[0,0,4,0]])
# übergang = np.array([[1,1,1],[1,0,1],[1,1,1]])
# flow_c = [[übergang*0.5,1],[übergang*0.3,2],[übergang*0.9,1],[übergang*0.1,1]]
# start = np.zeros([200,200,4])
# start[:,:,0] = 1
# start[50,:]=[0,0,1,0]
# start[5:10,5:10] = [0,1,0,0]
# test = simulation(start,300, flow_m, flow_c)
# test.run()
# test.generate_images()
# for i in range(0,300,50):
#     plt.imshow(test.images[i])
#     plt.show()

# ----------------------------------------------Beispiel Initialisierung 3------------------------------------------------------------------
# 1D Case
# rules = [0,1,1,1,1,0,0,0]
#
# iterations = 300
# start = np.zeros(300)
# start[125:150] = 1
# rule30 = oneD_cellular_automata(iterations,rules,start)
# rule30.run()
# plt.imshow(rule30.data[:,1:-1] ,cmap = "gray")
# plt.show()
#
# ----------------------------------------------Beispiel Initialisierung 4------------------------------------------------------------------
#
iterations = 10
start = np.zeros([5, 5])
start[3, :5] = 1

conways = conways_game_of_life(start, iterations)
plt.imshow(conways.data[0])
plt.show()
conways.run()
plt.imshow(conways.data[0])
plt.show()
for i in range(conways.iterations):
    plt.imshow(conways.data[i], cmap="gray")
    plt.show()
