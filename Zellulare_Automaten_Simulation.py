import numpy as np
import matplotlib.pyplot as plt
import math
from froll import dfroll2d
from froll import froll2d


# Allgemeine Simulationsklasse für das Informatikprojekt
# LK Winkler 2021 Q4 KKOS
# Mit Beisppeilintialisierungen am Ende des Programms

# Grundlegende Datenstruktur:
# Eine Simulation wird als 4D Array aufgefasst mit:
# 1 Zeitdimension     (Zeit)
# 2 Raumdimensionen   (Board)
# 1 Zustandsdimension (Zustände)


# Zwischen den verschiedenen Zuständen lässt sich mithilfe einer Flow-Matrix
# die Richtung und der Typ (jeder Typ erhält einen eindeutiger int Wert) des Flusses beschreiben
# Die Typen werden in einem Nachbarschaftarray gespeichert und bestehen wiederum
# aus 2D Arrays, welche eine Wahrscheinlichkeit zur Übertragung ausgehend vom
# Mittelpunkt des Arrays beinhalten

# Glossar:
# Board: Array der Zustände einer Simulation zu einem Zeitpunkt t
# Nachbarschaft: Die Zellen, welche für einen Zustandsübergang relevant sind
# Zustandsübergang: Wechsel des Zustandes einer Zelle für einen Zeitschritt t


# Zur Initialisierung erhält die Klasse, den Startzustand des Boards (data[0]),
# die Vollständige Flowmatrix(0 reserviert als kein Fluss), das FLowchart, besteht aus der Übertragungswahrscheinlichkeit und dem Träger

# Ausführlichere Erklärung zu den Datentypen in der Modellierung abgebildet

class simulation:
    def __init__(self, starting_conditions, iterations, flow_matrix, flow_chart):
        """
        :param starting_conditions: Board zum Zeitpunkt t=0
        :param iterations: Anzahl der auszuführenden Zeitschritten
        :param flow_matrix: Zustandsübergänge
        :param flow_chart:  Art der einzelnen Zustandsübergängen
        """
        self.iter = iterations
        # Initialisierung des Arrays zur Speicherung der Simulation:
        self.data = np.zeros(
            [iterations, starting_conditions.shape[0], starting_conditions.shape[1], starting_conditions.shape[2]])
        self.data[0] = starting_conditions
        self.images = "Images not yet generated"

        # Initialisierung der verschiedenen Übertragungen:
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
            # Array umgewandelt, welches die Koordinaten, sowie den Eintrag speichert:
            flow_chart[i][0] = temp
        self.flow = []
        for i in range(flow_matrix.shape[0]):
            for j in range(flow_matrix.shape[1]):
                if flow_matrix[i, j] != 0:
                    self.flow.append(flow_chart[flow_matrix[i, j] - 1])
                    self.flow[-1].append([i, j])

    def spread(self, board, candidates, flow_m):
        """
        Spiegelt die Übertragung für einen  Zeitschritt und einen Zustandstyp wieder
        :param board: Aktuelle Zustände nd.array mxnxz
        :param candidates: Potentielle Zellen für den Übergang
        :param flow_m: die umgeformte Flow Matrix
        :return: die entstandenen Zustandsübergänge
        """

        random = np.random.rand(board.shape[0], board.shape[1])
        new_cells = np.zeros([board.shape[0], board.shape[1]])
        # Verschiebung für jedes ELement der Nachbarschafts Matrix:
        for i in range(len(flow_m[0])):
            temp = dfroll2d((random + flow_m[2][i]) * board, [int(flow_m[0][i]), int(flow_m[1][i])])
            temp = temp.astype(int)
            # Alle Werte größer 1 --> 1:
            new_cells = (new_cells + temp).astype(bool)
        return new_cells * candidates

    def run(self):
        """"
        Ruft die Spread Funktion für jeden Zeitschritt und jeden Zustand auf und speicher die Zustände des Bopards im Data Array
        """
        for i in range(1, self.iter, 1):
            self.data[i] = self.data[i - 1]
            for j in range(len(self.flow)):
                temp = self.spread(self.data[i - 1, :, :, self.flow[j][1]], self.data[i - 1, :, :, self.flow[j][2][0]],
                                   self.flow[j][0])
                self.data[i, :, :, self.flow[j][2][0]] = self.data[i, :, :, self.flow[j][2][0]] - temp
                self.data[i, :, :, self.flow[j][2][1]] = self.data[i, :, :, self.flow[j][2][1]] + temp

    def get_data(self, t: int):
        """
        Einfache get Methode
        Gibt das Board zum Zeitpunkt t zurück. Ist t größer als die Anzahl der Iteration gibt das letzte Element aus.
        Ist t kleiner 0 gibt das t=0 aus.

        :param t: Zeitpunkt t, int
        :return: Der Zustand des Boards zum Zeitpunkt t
        """

        if t > self.iter - 1:
            return self.data[-1]
        elif t < 0:
            return self.data[0]
        else:
            return self.data[t]

    def get_image(self, t: int):
        """
        Einfache get Methode

        Edgecases analog zu get_data
        :param t: Zeitpunkt t
        :return: die RGB Matrix der aktuellen Zustände des Boards zum Zeitpunkt t
        """
        if t > self.iter - 1:
            return self.images[-1]
        elif t < 0:
            return self.images[0]
        else:
            return self.images[t]

    def generate_graph(self):
        """"
        :return: für jede Spalte die Summe der Zellen im jeweiligen Zustand zum Zeitpunkt t
        """
        graph = np.sum(self.data, (1, 2))
        return graph.transpose()

    def generate_colors(self):
        '''
        Die Farben für die Image Generation
        mxnxk --> mxnx3
        '''
        self.images = np.zeros(list(self.data.shape[:3]) + [3])
        colors = np.zeros([self.data.shape[3], 3])
        # Versucht die "Farbsistanz" zu maximieren, sehr naiver Ansatz
        for i in range(self.data.shape[3]):
            colors[i][0] = i * 1 / self.data.shape[3]
            colors[i][1] = 1 - i * 1 / self.data.shape[3]
            colors[i][2] = 1 - i * 1 / self.data.shape[3]
        return colors

    def generate_images(self, colors):
        """
        Generiert die Images mit gegebenen Bildern
        :param colors: RGB Werte für jeden Zustand in iterable
        """
        self.images = np.zeros(list(self.data.shape[:3]) + [3])
        for i in range(len(colors)):
            self.images[self.data[:, :, :, i] == 1] = colors[i]


class oneD_cellular_automata:

    def __init__(self, iterations, rules, start):
        """"
        :param rules : Regeln für die Simulation durch abdeckung aller möglichen Zustände
        :param start: Anfangsbedinbgungen im Array, Wichtig 1 Zelle Rand an beiden Seiten
        """""
        self.iterations = iterations
        self.rules = rules
        self.start = start
        self.data = np.zeros([iterations, start.shape[0]])
        self.data[0] = start

    def f(self, y, x, z):
        """"
        Modellierung der Zustandsübergänge für jed Zelle
        :return: Der neue Zustand in ABhängigkeit der Nachbarschaft
        """
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


# Mir wurde von einem Mitschüler gesagt, dass man keine Zellulären Automaten ohne Conways Game of Life macht,
class conways_game_of_life:
    def __init__(self, start, iterations):
        self.iterations = iterations
        self.data = np.zeros([iterations, start.shape[0], start.shape[1]])
        self.data[0] = start

    def rules(self, array):
        # Berechnung der Anzahl der Zellen in der Nachbarschaft einer Zelle:
        convolution = np.zeros(array.shape)
        for i in range(-1, 2, 1):
            for j in range(-1, 2, 1):
                convolution = convolution + froll2d(array, [i, j])
        convolution = convolution - array
        # Regeln für die einzelnen Zellen:
        array[convolution < 2] = 0
        array[convolution > 3] = 0
        array[convolution == 3] = 1
        return array

    def run(self):
        # Berechnung der neuen Zuständen für jeden Zeitschritt
        for i in range(1, self.iterations, 1):
            self.data[i] = self.rules(np.copy(self.data[i - 1]))


"""""------------------------------------------------Beispielinitialisierung SIR-Modell:------------------------------------------------------
Ein beispielhafte Anwendung wäre das SIR-Modell (mit räumlicher Beschränkung) soll stark vereinfacht die Verbreitung von Krankenheiten
in  einer festen Bevölkerung modellieren, Jede Zelle steht für eine Person und hat zu jedem Zeitpunkt t eine der folgenden Eigenschaften:
Hierbei gibt es 3 Zustände:
1: Suscepteble (infizierbar)
2: Infective   (infiziert)
3: Recoverd    (immun)
Der Fluss hat die From S-(I)->I-(I)->R
Wobei -(I)->, dafür steht, dass die Infektion von infizierten Zellen ausgelöst wird, bzw. die Erholung auch bei infizierten Zellenabläuft
Und läuft wie folgt ab:
Eine infizierte Zelle kann anliegende Zellen infizieren
Eine Zelle wird immun mit einer gewissen Wahrscheinlichkeit"""
# flow_m = np.array([[0,1,0],[0,0,2],[0,0,0]])#Flow-Matrix
# infection = np.array([[1,1,1],[1,0,1],[1,1,1]])*0.3#Nachbarschaft und Wahrscheinlichkeit für die Infektion
# recovery = np.array([0.6])#Nachabrschaft für die Erholung
# flow_c = [[infection,1],[recovery,1]]#Flow-Chart
#
# start = np.zeros([200,200,3])#Festlegung der Größe des Boards
# start[:,:] = [1,0,0]# Festlegung der Susceptibles
# start[50:55,50:55] = [0,1,0]#Festlegung der anfänglichen Infizierten
# start[100:105,100:105] = [0,1,0]
# sir = simulation(start, 300, flow_m, flow_c)
# sir.run()
# sir.generate_images(colors = [[1,0,0],[0,1,0],[0,0,1]])
# for i in range(0,300,50):
#     plt.imshow(sir.images[i])
#     plt.show()
# sir.generate_graph()
""" ----------------------------------------------Beispiel Initialisierung 2------------------------------------------------------------------
Beispiel Simulation für eine Simulation mit mehr Zuständen (ohne praktische Anwendung)"""
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

""""----------------------------------------------Beispiel Initialisierung 3------------------------------------------------------------------
Rule 30 1D Zellulärer Automat Beispuelinitialisierung
"""
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
"""----------------------------------------------Beispiel Initialisierung 4------------------------------------------------------------------
Beispielinitialisierung für Conways game of life
"""
#
# iterations = 10
# start = np.zeros([5, 5])
# start[3, :3] = 1
#
# conways = conways_game_of_life(start, iterations)
# conways.run()
# for i in range(conways.iterations):
#     plt.imshow(1 - conways.data[i], cmap="gray")
#     plt.show()

