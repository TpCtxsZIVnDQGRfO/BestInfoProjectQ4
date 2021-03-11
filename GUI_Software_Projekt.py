#!/usr/bin/env python
# coding: utf-8

from tkinter import *
from tkinter import messagebox
from tkinter.filedialog import askopenfilename, asksaveasfilename
from Zellulare_Automaten_Simulation import *
from NodeSimulation import *
from ast import literal_eval

import numpy as np
import time
import threading

import matplotlib
matplotlib.use("TkAgg")

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
import matplotlib.animation as animation

from playsound import playsound


# Globale Variablen
data_list = [] # Datenstruktur: [ID, Name der Simulation, Daten Array, Filepath, Frame]
#  Daten Array: Simulations-Typ, x-Length, y-Length, p0_coordinates, steps, infectionrate, recoveryrate
toolbox = [-1, -1]
# current_simulation (-1 keine Simulation ausgewählt), Load-Counter



# Fenster initialisieren
fenster = Tk()
fenster.title("Der Simulator-Simulator")
fenster.resizable(0, 0)
fenster.config(bg='white')

# Fenstergröße
fenster.geometry("675x675")

# To-Do-List
# - weiß werden der p0_coordinates_tf bzw. rot werden
# - Speicherung der p0_coordinates in schönem Format zum Wiederöffnen
# - Bug bei Copy-Pasting in Infection-Field


#class Frame Rechteck
class input_simulationA:
    def __init__(self, ID, name, len_x, len_y, p0_coordinates, steps, infection, recovery):
        self.ID = ID
        self.name = name
        self.len_x = len_x
        self.len_y = len_y
        self.p0_coordinates = p0_coordinates
        self.steps = steps
        self.infection = infection
        self.recovery = recovery

        self.frame = Frame(fenster)
        self.frame.config(bg='red')

    def create_frame(self):
        # Frames
        grafic_frame = Frame(master=self.frame, bg='green')
        grafic_frame.pack(side=TOP, padx='5', pady='5', fill=BOTH)

        name_frame = Frame(master=self.frame, bg='yellow')
        name_frame.pack(side='top', padx='5', pady='5', fill=X)

        components_frame = Frame(master=self.frame, bg='green')
        components_frame.pack(padx='5', pady='5', fill=X)

        label_frame = Frame(master=components_frame, bg='magenta')
        label_frame.pack(side='left', padx='5', pady='5')

        tf_frame = Frame(master=components_frame, bg='red')
        tf_frame.pack(side='right', padx='5', pady='5')

        start_frame = Frame(master=self.frame, bg='blue')
        start_frame.pack(side='top', padx='5', pady='5', fill=X)


        # Grafik
        data = np.zeros([200,200,3])
        data[:,:] = [1,0,0]

        image = data
        fig = plt.figure(figsize=(5,4))
        im = plt.imshow(image)
        ax = plt.gca()
        ax.set_xticks([0])
        ax.set_yticks([0])

        # a tk.DrawingArea
        canvas = FigureCanvasTkAgg(fig, master=grafic_frame)
        canvas.get_tk_widget().pack(side=TOP, fill=BOTH, anchor='w')
        canvas.draw()
        plt.close()


        # Grafik-Update-Funktion: Wird aufgerufen, wenn der Slider bewegt wird
        def grafic_change():
            try:
                data = np.zeros([self.len_x,self.len_x,3]) # Verändert für gleich große Grid-Seiten
                data[:,:] = [1,0,0]
                for i in self.p0_coordinates:
                    data[i[0],i[1]] = [0,1,0]

                im.set_data(data)
                len_x_tf.config(bg="white")
                #p0_coordinates_tf.config(bg="white")

            except:
                len_x_tf.config(bg="red")
                #p0_coordinates_tf.config(bg="red")

            canvas.draw()

        '''# Erstmal nicht in Benutzung
        def motion(event):
            x, y = event.x, event.y
            print([x,y])

        fenster.bind('<ButtonRelease-1>', motion)
        fenster.bind('<Button-1>', motion)
        '''
        
        def motion(event):
            len_x_tf.icursor("end")
            len_y_tf.icursor("end")
            steps_tf.icursor("end")
            infection_tf.icursor("end")
            recovery_tf.icursor("end")

        
        fenster.bind('<Button-1>', motion)
        fenster.bind('<ButtonRelease-1>', motion)
        fenster.bind('<Left>', motion)
        fenster.bind('<Right>', motion)
        fenster.bind('<BackSpace>', motion)
        

        # Funktionen zur Einstellung einer maxlength für die Textfelder und Regulierung der erlaubten Zeichen
        def limitSizeX(*args):
            value = len_x_in.get()
            # löschen aller nicht erlaubten Zeichen
            i = 0
            while(i<len(value)):
                if(value[i] not in "0123456789"):
                    value=value[:i]+value[i+1:]
                else:
                    i+=1
            # Der Inhalt darf nicht mit einer 0 beginnen
            value = value[:3]
            # nicht mehr als drei Zeichen
            while(len(value)>0 and value[0]=="0"):
                value = value[1:]
            len_x_in.set(value)
            # Wenn kein Inhalt im Eingabefeld ist, soll intern 0 gespeichert werden
            if(len(value)==0):
                value=0
            self.len_x = int(value)
            # Überprüfung P0-Koordinaten nach Grid Änderung
            try:
                s=literal_eval(p0_coordinates_in.get())
                b = [len(i)==2 and i[0]<self.len_x and i[1]<self.len_x for i in s] # Verändert für gleich große Grid-Seiten
                if(False not in b):
                    p0_coordinates_tf.config(bg="white")
                    self.p0_coordinates = s
                else:
                    p0_coordinates_tf.config(bg="red")
            except:
                p0_coordinates_tf.config(bg="red")

            grafic_change()

        def limitSizeY(*args):
            value = len_y_in.get()
            # löschen aller nicht erlaubten Zeichen
            i = 0
            while(i<len(value)):
                if(value[i] not in "0123456789"):
                    value=value[:i]+value[i+1:]
                else:
                    i+=1
            # nicht mehr als drei Zeichen
            value = value[:3]
            # Der Inhalt darf nicht mit einer 0 beginnen
            while(len(value)>0 and value[0]=="0"):
                value = value[1:]
            len_y_in.set(value)
            # Wenn kein Inhalt im Eingabefeld ist, soll intern 0 gespeichert werden
            if(len(value)==0):
                value=0
            self.len_y = int(value)
            # Überprüfung Koordinaten nach Grid Änderung
            try:
                s=literal_eval(p0_coordinates_in.get())
                b = [len(i)==2 and i[0]<self.len_x and i[1]<self.len_y for i in s]
                if(False not in b):
                    p0_coordinates_tf.config(bg="white")
                    self.p0_coordinates = s
                else:
                    p0_coordinates_tf.config(bg="red")
            except:
                p0_coordinates_tf.config(bg="red")

            grafic_change()


        def limitSizeP0Coor(*args):
            value = p0_coordinates_in.get()
            # löschen aller nicht erlaubten Zeichen
            i = 0
            while(i<len(value)):
                if(value[i] not in "0123456789[],"):
                    value=value[:i]+value[i+1:]
                else:
                    i+=1
            p0_coordinates_in.set(value)
            # Überprüfung der Eingabe der Koordinaten
            try:
                # richtige Klammerung und Kommasetzung
                s=literal_eval(value)
                # Koordinatenpaare nicht länger als 2 und Koordinaten innerhalb der Grid-Länge
                b = [len(i)==2 and i[0]<self.len_x and i[1]<self.len_x for i in s] # Verändert für gleich große Grid-Seiten

                c = [(len(i)==4 or len(i)==2) and i[0]<self.len_x and i[1]<self.len_x for i in s]

                if(False not in b):
                    p0_coordinates_tf.config(bg="white")
                    self.p0_coordinates = s
                elif(False not in c):
                    p0_coordinates_tf.config(bg="white")
                    new_coord = []
                    for i in range(len(b)):
                        if(b[i]==True):
                            new_coord.append(s[i])
                        elif(b[i]==False and c[i]==True):
                            w = [s[i][0],s[i][2]]
                            v = [s[i][1],s[i][3]]
                            for j in range(min(w),max(w)+1):
                                for k in range(min(v),max(v)+1):
                                    new_coord.append([j,k])
                    self.p0_coordinates = new_coord
                else:
                    p0_coordinates_tf.config(bg="red")
            except:
                p0_coordinates_tf.config(bg="red")

            grafic_change()

        def limitSizeSteps(*args):
            value = steps_in.get()

            # löschen aller nicht erlaubten Zeichen
            i = 0
            while(i<len(value)):
                if(value[i] not in "0123456789"):
                    value=value[:i]+value[i+1:]
                else:
                    i+=1
            # nicht mehr als drei Zeichen
            value = value[:3]
            # Der Inhalt darf nicht mit einer 0 beginnen
            while(len(value)>0 and value[0]=="0"):
                value = value[1:]
            steps_in.set(value)
            # Wenn kein Inhalt im Eingabefeld ist, soll intern 0 gespeichert werden
            if(len(value)==0):
                value=0
            self.steps = int(value)

        def limitSizeInf(*args):
            value = infection_in.get()
            # nicht mehr als fünf Zeichen
            value = value[2:5]
            # löschen aller nicht erlaubten Zeichen
            i = 0
            while(i<len(value)):
                if(value[i] not in "0123456789"):
                    value=value[:i]+value[i+1:]
                else:
                    i+=1
            # Vor den Inhalt "0." setzen, damit eine Eingabe der Form 0.xxx vorliegt
            value="0."+value
            infection_in.set(value)
            self.infection = float(value)
            # Cursor ans Ende setzen, damit man nicht, wenn man "0." wegmachen möchte dazwischen , d.h. "0|.", ist mit dem Cursor, (funktioniert nicht ganz)


        def limitSizeRec(*args):
            value = recovery_in.get()
            # nicht mehr als fünf Zeichen
            value = value[2:5]
            # löschen aller nicht erlaubten Zeichen
            i = 0
            while(i<len(value)):
                if(value[i] not in "0123456789"):
                    value=value[:i]+value[i+1:]
                else:
                    i+=1
            # Vor den Inhalt "0." setzen, damit eine Eingabe der Form 0.xxx vorliegt
            value="0."+value
            recovery_in.set(value)
            self.recovery = float(value)
            # Cursor ans Ende setzen, damit man nicht, wenn man "0." wegmachen möchte dazwischen , d.h. "0|.", ist mit dem Cursor, (funktioniert nicht ganz)


        def limitSizeName(*args):
            value = name_in.get()
            # nicht mehr als 20 Zeichen
            value = value[:20]
            # löschen aller nicht erlaubten Zeichen
            i = 0
            while(i<len(value)):
                if(value[i].lower() not in "abcdefghijktlmnopqrstuvwxyz _-"):
                    value=value[:i]+value[i+1:]
                else:
                    i+=1
            # Der Inhalt darf nicht mit einer " " beginnen
            while(len(value)>0 and value[0]==" "):
                value = value[1:]
            name_in.set(value)
            # Wenn kein Inhalt im Eingabefeld ist, soll intern "Untitled" gespeichert werden
            if(len(value)==0):
                value="Untitled"
            self.name = value

            if(toolbox[0] == self.ID):
                fenster.title(self.name)
                data_list[toolbox[0]][4].update_data_list()
                simulation_menu.entryconfig(toolbox[0], label=data_list[toolbox[0]][4].name)

        # Initialisierung der oberen Überprüfungsmethoden
        len_x_in = StringVar()
        len_x_in.trace('w',limitSizeX)

        len_y_in = StringVar()
        len_y_in.trace('w',limitSizeY)

        steps_in = StringVar()
        steps_in.trace('w',limitSizeSteps)

        infection_in = StringVar()
        infection_in.trace('w',limitSizeInf)

        recovery_in = StringVar()
        recovery_in.trace('w',limitSizeRec)

        p0_coordinates_in = StringVar()
        p0_coordinates_in.trace('w',limitSizeP0Coor)

        name_in = StringVar()
        name_in.trace('w',limitSizeName)

        # Starten der Simulation
        def start_button_action():
            try:
                # Flow-Matrix
                flow_m = np.array([[0,1,0],[0,0,2],[0,0,0]])
                # Ausbreitungsrate
                infection = np.array([[1,1,1],[1,0,1],[1,1,1]])*self.infection
                # Erholungsrate
                recovery = np.array([self.recovery])
                # Flow-Chart
                flow_c = [[infection,1],[recovery,1]]
                # Festlegung der Größe des Boards
                start = np.zeros([self.len_x,self.len_x,3]) # Verändert für gleich große Grid-Seiten
                start[:,:] = [1,0,0]
                # Festlegung der anfänglichen Infizierten
                for i in self.p0_coordinates:
                    start[i[0],i[1]] = [0,1,0]

                sir = simulation(start, self.steps, flow_m, flow_c)
                sir.run()
                sir.generate_images()
                out = output_simulationA(self.name, self.steps, self.len_x, self.len_y, sir)

            except:
                print("Unexpected error:", sys.exc_info()[0])



        # Komponenten
        name_tf = Entry(name_frame, width=50, relief=SOLID, textvariable=name_in, justify='center')
        name_tf.insert(0, self.name)

        len_x_label = Label(label_frame, text="Grid-Length", relief=SOLID, borderwidth = 1, anchor='w', width=30, bg='white') # Verändert für gleich große Grid-Seiten
        len_y_label = Label(label_frame, text="Grid-Length-y", relief=SOLID, borderwidth = 1, anchor='w', width=30, bg='white')
        p0_coordinates_label = Label(label_frame, text="p0-Coordinates", relief=SOLID, borderwidth = 1, anchor='w', width=30, bg='white')
        steps_label = Label(label_frame, text="Stepnumber", relief=SOLID, borderwidth = 1, anchor='w', width=30, bg='white')
        infection_label = Label(label_frame, text="Infectionrate", relief=SOLID, borderwidth = 1, anchor='w', width=30, bg='white')
        recovery_label = Label(label_frame, text="Recoveryrate", relief=SOLID, borderwidth = 1, anchor='w', width=30, bg='white')

        len_x_tf = Entry(tf_frame, width=35, relief=SOLID, textvariable=len_x_in)
        len_y_tf = Entry(tf_frame, width=35, relief=SOLID, textvariable=len_y_in)
        p0_coordinates_tf = Entry(tf_frame, width=35, relief=SOLID, textvariable=p0_coordinates_in)
        steps_tf = Entry(tf_frame, width=35, relief=SOLID, textvariable=steps_in)
        infection_tf = Entry(tf_frame, width=35, relief=SOLID, textvariable=infection_in)
        recovery_tf = Entry(tf_frame, width=35, relief=SOLID, textvariable=recovery_in)

        # Befüllung der Textfelder mit dem Inhalt der Simulationen
        len_x_tf.insert(0, str(self.len_x))
        len_y_tf.insert(0, str(self.len_y))
        p0_coordinates_tf.insert(0, str(self.p0_coordinates))
        steps_tf.insert(0, str(self.steps))
        infection_tf.insert(0, str(self.infection))
        recovery_tf.insert(0, str(self.recovery))

        # Positionierung der Komponenten
        start_button = Button(start_frame, text="start", command=start_button_action, width=30)

        label_array = [len_x_label, steps_label, infection_label, recovery_label, p0_coordinates_label] # Verändert für gleich große Grid-Seiten
        tf_array = [len_x_tf, steps_tf, infection_tf, recovery_tf, p0_coordinates_tf] # Verändert für gleich große Grid-Seiten

        name_tf.pack(side=TOP, ipady=5, ipadx=10)

        for i in range(len(label_array)):
            label_array[i].pack(side=TOP, ipady=5, ipadx=10)

        for i in range(len(tf_array)):
            tf_array[i].pack(side=TOP, ipady=5, ipadx=10)

        start_button.pack(ipady=5, ipadx=10)

    # Methode zur Übertragung der veränderten Attribute der Simulation in das data_list-Array
    def update_data_list(self):
        pos = -1
        for i in range(len(data_list)):
            if(data_list[i][0] == self.ID):
                pos = i
                break
        data_list[pos][1] = self.name
        data_list[pos][2][1] = self.len_x
        data_list[pos][2][2] = self.len_y
        data_list[pos][2][3] = self.p0_coordinates
        data_list[pos][2][4] = self.steps
        data_list[pos][2][5] = self.infection
        data_list[pos][2][6] = self.recovery


'''
# Code für eine Beispiel Initialisierung einer Simulation

frame_test = input_simulationA(0, "Nicer Dicer", 200, 400, [[50,50],[51,351]], 150, 0.6, 0.3)
frame_test.create_frame()
frame_test.frame.pack(fill=BOTH, expand=True, side=BOTTOM, anchor=S)
'''

#class Frame Nodes-Simulation
class input_simulationB:
    # Startbedingungen der Nodes, flowchart, Größe des Canvas, Auflösung der Visualisierung, Farben der Nodes in den verschiedenen Zuständen, Geschwindigkeit der Nodes, Framerate des Videos, Videolänge, Anzahl und Positionen der Barrieren, maximale Entfernung, mit der zwei Nodes noch verbunden sind, Maximalabstand, den Nodes zu ihrem Startpunkt haben können, Visuals der Barrieren und Verbindungen
    def __init__(self, ID, name, frames, node_number, infected_number, node_speed, hospital_number, hospital_capacity, recovery_time, hospital_distance, infection_radius, movement_radius, barriers = [], canvas_x = 1600, canvas_y = 900, resolution_x = 1600, resolution_y = 900):
        self.ID = ID
        self.name = name
        self.frames = frames
        
        self.node_number = node_number
        self.infected_number = infected_number
        self.node_speed = node_speed
        
        self.hospital_number = hospital_number
        self.hospital_capacity = hospital_capacity
        self.recovery_time = recovery_time
        self.hospital_distance = hospital_distance
        
        self.infection_radius = infection_radius
        self.movement_radius = movement_radius
        
        self.barriers = barriers
        
        self.canvas_x = canvas_x
        self.canvas_y = canvas_y
        self.resolution_x = resolution_x
        self.resolution_y = resolution_y

        self.frame = Frame(fenster)
        self.frame.config(bg='red')

    def create_frame(self):
        # Frames
        grafic_frame = Frame(master=self.frame, bg='green')
        grafic_frame.pack(side=TOP, padx='5', pady='5', fill=BOTH)

        name_frame = Frame(master=self.frame, bg='yellow')
        name_frame.pack(side='top', padx='5', pady='5', fill=X)

        components_frame = Frame(master=self.frame, bg='green')
        components_frame.pack(padx='5', pady='5', fill=X)

        label_frame = Frame(master=components_frame, bg='magenta')
        label_frame.pack(side='left', padx='5', pady='5')

        tf_frame = Frame(master=components_frame, bg='red')
        tf_frame.pack(side='right', padx='5', pady='5')

        start_frame = Frame(master=self.frame, bg='blue')
        start_frame.pack(side='top', padx='5', pady='5', fill=X)

        # Funktionen zur Einstellung einer maxlength für die Textfelder und Regulierung der erlaubten Zeichen
        def limitSizeName(*args):
            value = name_in.get()
            # nicht mehr als 20 Zeichen
            value = value[:20]
            # löschen aller nicht erlaubten Zeichen
            i = 0
            while(i<len(value)):
                if(value[i].lower() not in "abcdefghijktlmnopqrstuvwxyz _-"):
                    value=value[:i]+value[i+1:]
                else:
                    i+=1
            # Der Inhalt darf nicht mit einer " " beginnen
            while(len(value)>0 and value[0]==" "):
                value = value[1:]
            name_in.set(value)
            # Wenn kein Inhalt im Eingabefeld ist, soll intern "Untitled" gespeichert werden
            if(len(value)==0):
                value="Untitled"
            self.name = value

            if(toolbox[0] == self.ID):
                fenster.title(self.name)
                data_list[toolbox[0]][4].update_data_list()
                simulation_menu.entryconfig(toolbox[0], label=data_list[toolbox[0]][4].name)
        
        def limitSizeFrames(*args):
            value = frames_in.get()
            # löschen aller nicht erlaubten Zeichen
            i = 0
            while(i<len(value)):
                if(value[i] not in "0123456789"):
                    value=value[:i]+value[i+1:]
                else:
                    i+=1
            # Der Inhalt darf nicht mit einer 0 beginnen
            value = value[:3]
            # nicht mehr als drei Zeichen
            while(len(value)>0 and value[0]=="0"):
                value = value[1:]
            frames_in.set(value)
            # Wenn kein Inhalt im Eingabefeld ist, soll intern 10 gespeichert werden
            if(len(value)==0):
                value=10
            self.frames = int(value)

        def limitSizeNodeNumber(*args):
            value = node_number_in.get()
            # löschen aller nicht erlaubten Zeichen
            i = 0
            while(i<len(value)):
                if(value[i] not in "0123456789"):
                    value=value[:i]+value[i+1:]
                else:
                    i+=1
            # Der Inhalt darf nicht mit einer 0 beginnen
            value = value[:3]
            # nicht mehr als drei Zeichen
            while(len(value)>0 and value[0]=="0"):
                value = value[1:]
            node_number_in.set(value)
            # Wenn kein Inhalt im Eingabefeld ist, soll intern 0 gespeichert werden
            if(len(value)==0):
                value=0
            self.node_number = int(value)
            if(self.node_number < self.infected_number):
                infected_number_tf.config(bg="red")
            else:
                infected_number_tf.config(bg="white")

        def limitSizeInfectedNumber(*args):
            value = infected_number_in.get()
            # löschen aller nicht erlaubten Zeichen
            i = 0
            while(i<len(value)):
                if(value[i] not in "0123456789"):
                    value=value[:i]+value[i+1:]
                else:
                    i+=1
            # Der Inhalt darf nicht mit einer 0 beginnen
            value = value[:3]
            # nicht mehr als drei Zeichen
            while(len(value)>0 and value[0]=="0"):
                value = value[1:]
            infected_number_in.set(value)
            # Wenn kein Inhalt im Eingabefeld ist, soll intern 0 gespeichert werden
            if(len(value)==0):
                value=0
            if(int(value) <= self.node_number):
                infected_number_tf.config(bg="white")
            else:
                infected_number_tf.config(bg="red")
            self.infected_number = int(value)

        def limitSizeNodeSpeed(*args):
            value = node_speed_in.get()
            # löschen aller nicht erlaubten Zeichen
            i = 0
            while(i<len(value)):
                if(value[i] not in "0123456789"):
                    value=value[:i]+value[i+1:]
                else:
                    i+=1
            # Der Inhalt darf nicht mit einer 0 beginnen
            value = value[:2]
            # nicht mehr als 2 Zeichen
            while(len(value)>0 and value[0]=="0"):
                value = value[1:]
            node_speed_in.set(value)
            # Wenn kein Inhalt im Eingabefeld ist, soll intern 0 gespeichert werden
            if(len(value)==0):
                value=0
            self.node_speed = int(value)

        def limitSizeHospitalNumber(*args):
            value = hospital_number_in.get()
            # löschen aller nicht erlaubten Zeichen
            i = 0
            while(i<len(value)):
                if(value[i] not in "0123456789"):
                    value=value[:i]+value[i+1:]
                else:
                    i+=1
            # Der Inhalt darf nicht mit einer 0 beginnen
            value = value[:2]
            # nicht mehr als 2 Zeichen
            while(len(value)>0 and value[0]=="0"):
                value = value[1:]
            hospital_number_in.set(value)
            # Wenn kein Inhalt im Eingabefeld ist, soll intern 0 gespeichert werden
            if(len(value)==0):
                value=10
            self.hospital_number = int(value)

        def limitSizeHospitalCapacity(*args):
            value = hospital_capacity_in.get()
            # löschen aller nicht erlaubten Zeichen
            i = 0
            while(i<len(value)):
                if(value[i] not in "0123456789"):
                    value=value[:i]+value[i+1:]
                else:
                    i+=1
            # Der Inhalt darf nicht mit einer 0 beginnen
            value = value[:2]
            # nicht mehr als 2 Zeichen
            while(len(value)>0 and value[0]=="0"):
                value = value[1:]
            hospital_capacity_in.set(value)
            # Wenn kein Inhalt im Eingabefeld ist, soll intern 0 gespeichert werden
            if(len(value)==0):
                value=0
            self.hospital_capacity = int(value)

        def limitSizeRecoveryTime(*args):
            value = recovery_time_in.get()
            # löschen aller nicht erlaubten Zeichen
            i = 0
            while(i<len(value)):
                if(value[i] not in "0123456789"):
                    value=value[:i]+value[i+1:]
                else:
                    i+=1
            # Der Inhalt darf nicht mit einer 0 beginnen
            value = value[:2]
            # nicht mehr als 2 Zeichen
            while(len(value)>0 and value[0]=="0"):
                value = value[1:]
            recovery_time_in.set(value)
            # Wenn kein Inhalt im Eingabefeld ist, soll intern 0 gespeichert werden
            if(len(value)==0):
                value=10
            self.recovery_time = int(value)

        def limitSizeHospitalDistance(*args):
            value = hospital_distance_in.get()
            # löschen aller nicht erlaubten Zeichen
            i = 0
            while(i<len(value)):
                if(value[i] not in "0123456789"):
                    value=value[:i]+value[i+1:]
                else:
                    i+=1
            # Der Inhalt darf nicht mit einer 0 beginnen
            value = value[:3]
            # nicht mehr als drei Zeichen
            while(len(value)>0 and value[0]=="0"):
                value = value[1:]
            hospital_distance_in.set(value)
            # Wenn kein Inhalt im Eingabefeld ist, soll intern 10 gespeichert werden
            if(len(value)==0):
                value=10
            self.hospital_distance = int(value)

        def limitSizeInfectionRadius(*args):
            value = infection_radius_in.get()
            # löschen aller nicht erlaubten Zeichen
            i = 0
            while(i<len(value)):
                if(value[i] not in "0123456789"):
                    value=value[:i]+value[i+1:]
                else:
                    i+=1
            # Der Inhalt darf nicht mit einer 0 beginnen
            value = value[:3]
            # nicht mehr als drei Zeichen
            while(len(value)>0 and value[0]=="0"):
                value = value[1:]
            infection_radius_in.set(value)
            # Wenn kein Inhalt im Eingabefeld ist, soll intern 10 gespeichert werden
            if(len(value)==0):
                value=10
            self.infection_radius = int(value)

        def limitSizeMovementRadius(*args):
            value = movement_radius_in.get()
            # löschen aller nicht erlaubten Zeichen
            i = 0
            while(i<len(value)):
                if(value[i] not in "0123456789"):
                    value=value[:i]+value[i+1:]
                else:
                    i+=1
            # Der Inhalt darf nicht mit einer 0 beginnen
            value = value[:3]
            # nicht mehr als drei Zeichen
            while(len(value)>0 and value[0]=="0"):
                value = value[1:]
            movement_radius_in.set(value)
            # Wenn kein Inhalt im Eingabefeld ist, soll intern 10 gespeichert werden
            if(len(value)==0):
                value=10
            self.movement_radius = int(value)

        def limitSizeBarriers(*args):
            value = barriers_in.get()
            # löschen aller nicht erlaubten Zeichen
            i = 0
            while(i<len(value)):
                if(value[i] not in "0123456789[],"):
                    value=value[:i]+value[i+1:]
                else:
                    i+=1
            barriers_in.set(value)
            # Überprüfung der Eingabe der Koordinaten
            try:
                # richtige Klammerung und Kommasetzung
                s=literal_eval(value)
                # Koordinatenpaare nicht länger als 4 und Koordinaten innerhalb der Grid-Länge
                b = [len(i)==4 and i[0]<self.canvas_x and i[1]<self.canvas_y and i[2]<self.canvas_x and i[3]<self.canvas_y for i in s]

                if(False not in b):
                    barriers_tf.config(bg="white")
                    self.barriers = s
                else:
                    barriers_tf.config(bg="red")
            except:
                barriers_tf.config(bg="red")

        # Initialisierung der Textvariablen
        name_in = StringVar()
        name_in.trace('w',limitSizeName)
        
        frames_in = StringVar()
        frames_in.trace('w',limitSizeFrames)
        
        node_number_in = StringVar()
        node_number_in.trace('w',limitSizeNodeNumber)
        
        infected_number_in = StringVar()
        infected_number_in.trace('w',limitSizeInfectedNumber)
        
        node_speed_in = StringVar()
        node_speed_in.trace('w',limitSizeNodeSpeed)
        
        hospital_number_in = StringVar()
        hospital_number_in.trace('w',limitSizeHospitalNumber)
        
        hospital_capacity_in = StringVar()
        hospital_capacity_in.trace('w',limitSizeHospitalCapacity)
        
        recovery_time_in = StringVar()
        recovery_time_in.trace('w',limitSizeRecoveryTime)
        
        hospital_distance_in = StringVar()
        hospital_distance_in.trace('w',limitSizeHospitalDistance)
        
        infection_radius_in = StringVar()
        infection_radius_in.trace('w',limitSizeInfectionRadius)
        
        movement_radius_in = StringVar()
        movement_radius_in.trace('w',limitSizeMovementRadius)
        
        barriers_in = StringVar()
        barriers_in.trace('w',limitSizeBarriers)

        # Starten der Simulation
        def start_button_action():
            #start_button.config(state=DISABLED)            
            try:
                pos = -1
                for i in range(len(data_list)):
                    if(data_list[i][0] == self.ID):
                        pos = i
                        break
                data_list[pos][4].update_data_list()
                
                # Simulation Initialisieren

                
                flowchart = np.array([[0,0.05,0],[0,0,0.00025],[0,0,0]])
                
                sim = Simulation([],flowchart, 5, 10, 5, 90)    # Muss noch veränderbar gemacht werden
                
                sim.frames = data_list[pos][2][1]
                sim.canvas = [data_list[pos][2][12], data_list[pos][2][13]]
                sim.resolution = [data_list[pos][2][14], data_list[pos][2][15]]
                
                sim.addRandomNode(data_list[pos][2][2], [1,0,0])
                for i in range(data_list[pos][2][3]):               # Anfangsinfizierte
                    sim.nodes[i].state = [0,1,0]
                
                sim.speed = data_list[pos][2][4]
                sim.addRandomKH(data_list[pos][2][5], data_list[pos][2][6])
                
                sim.Behandlungsdauer = data_list[pos][2][7]
                sim.KHWeg = data_list[pos][2][8]
                sim.maxDist = data_list[pos][2][9]
                sim.movementRadius = data_list[pos][2][10]
                
                sim.barrierColour = "red" 
                sim.barrierWidth = 2
                sim.connecColour = "white"
                sim.connecWidth = 1

                for i in data_list[pos][2][11]:
                    sim.barriers.append([[i[0],i[1]],[i[2],i[3]]])

                
                frameArr = []
                for i in range(sim.frames):
                    sim.generate_connections()
                    frameArr.append(np.array(sim.visualComplete()))
                    sim.run(1)
                    print(i)

                    
                for pic in frameArr: #Rot- und Blaukanal werden getauscht
                    for i in range(len(pic)):
                        pic[i][:, [2, 0]] = pic[i][:, [0, 2]]

                Utility.cptv(frameArr,"video.mp4",sim.fps)

                print("Das Video wurde erstellt.")
                
            except:
                print("Unexpected error:", sys.exc_info()[0])

            #start_button.config(state=NORMAL)

        # Komponenten
        name_tf = Entry(name_frame, width=50, relief=SOLID, textvariable=name_in, justify='center')
        name_tf.insert(0, self.name)

        frames_label = Label(label_frame, text="Frames", relief=SOLID, borderwidth = 1, anchor='w', width=30, bg='white')
        node_number_label = Label(label_frame, text="Node number", relief=SOLID, borderwidth = 1, anchor='w', width=30, bg='white')
        infected_number_label = Label(label_frame, text="Infected number", relief=SOLID, borderwidth = 1, anchor='w', width=30, bg='white')
        node_speed_label = Label(label_frame, text="Node speed", relief=SOLID, borderwidth = 1, anchor='w', width=30, bg='white')
        hospital_number_label = Label(label_frame, text="Hospital number", relief=SOLID, borderwidth = 1, anchor='w', width=30, bg='white')
        hospital_capacity_label = Label(label_frame, text="Hospital capacity", relief=SOLID, borderwidth = 1, anchor='w', width=30, bg='white')
        recovery_time_label = Label(label_frame, text="Recovery time (in s)", relief=SOLID, borderwidth = 1, anchor='w', width=30, bg='white')
        hospital_distance_label = Label(label_frame, text="Hospital distance", relief=SOLID, borderwidth = 1, anchor='w', width=30, bg='white')
        infection_radius_label = Label(label_frame, text="Infection radius", relief=SOLID, borderwidth = 1, anchor='w', width=30, bg='white')
        movement_radius_label = Label(label_frame, text="Movement radius", relief=SOLID, borderwidth = 1, anchor='w', width=30, bg='white')
        barriers_label = Label(label_frame, text="Barriers", relief=SOLID, borderwidth = 1, anchor='w', width=30, bg='white')

        frames_tf = Entry(tf_frame, width=35, relief=SOLID, textvariable=frames_in)
        node_number_tf = Entry(tf_frame, width=35, relief=SOLID, textvariable=node_number_in)
        infected_number_tf = Entry(tf_frame, width=35, relief=SOLID, textvariable=infected_number_in)
        node_speed_tf = Entry(tf_frame, width=35, relief=SOLID, textvariable=node_speed_in)
        hospital_number_tf = Entry(tf_frame, width=35, relief=SOLID, textvariable=hospital_number_in)
        hospital_capacity_tf = Entry(tf_frame, width=35, relief=SOLID, textvariable=hospital_capacity_in)
        recovery_time_tf = Entry(tf_frame, width=35, relief=SOLID, textvariable=recovery_time_in)
        hospital_distance_tf = Entry(tf_frame, width=35, relief=SOLID, textvariable=hospital_distance_in)
        infection_radius_tf = Entry(tf_frame, width=35, relief=SOLID, textvariable=infection_radius_in)
        movement_radius_tf = Entry(tf_frame, width=35, relief=SOLID, textvariable=movement_radius_in)
        barriers_tf = Entry(tf_frame, width=35, relief=SOLID, textvariable=barriers_in)

        # Befüllung der Textfelder mit dem Inhalt der Simulationen
        frames_tf.insert(0, str(self.frames))
        node_number_tf.insert(0, str(self.node_number))
        infected_number_tf.insert(0, str(self.infected_number))
        node_speed_tf.insert(0, str(self.node_speed))
        hospital_number_tf.insert(0, str(self.hospital_number))
        hospital_capacity_tf.insert(0, str(self.hospital_capacity))
        recovery_time_tf.insert(0, str(self.recovery_time))
        hospital_distance_tf.insert(0, str(self.hospital_distance))
        infection_radius_tf.insert(0, str(self.infection_radius))
        movement_radius_tf.insert(0, str(self.movement_radius))
        barriers_tf.insert(0, str(self.barriers))

        # Positionierung der Komponenten
        start_button = Button(start_frame, text="start", command=start_button_action, width=30)

        label_array = [frames_label, node_number_label, infected_number_label, node_speed_label, hospital_number_label, hospital_capacity_label, recovery_time_label, hospital_distance_label, infection_radius_label, movement_radius_label, barriers_label]
        tf_array = [frames_tf, node_number_tf, infected_number_tf, node_speed_tf, hospital_number_tf, hospital_capacity_tf,recovery_time_tf, hospital_distance_tf, infection_radius_tf, movement_radius_tf, barriers_tf]

        name_tf.pack(side=TOP, ipady=5, ipadx=10)

        for i in range(len(label_array)):
            label_array[i].pack(side=TOP, ipady=5, ipadx=10)

        for i in range(len(tf_array)):
            tf_array[i].pack(side=TOP, ipady=5, ipadx=10)

        start_button.pack(ipady=5, ipadx=10)

    # Methode zur Übertragung der veränderten Attribute der Simulation in das data_list-Array
    def update_data_list(self):
        pos = -1
        for i in range(len(data_list)):
            if(data_list[i][0] == self.ID):
                pos = i
                break
        data_list[pos][1] = self.name
        data_list[pos][2][1] = self.frames
        data_list[pos][2][2] = self.node_number
        if(self.node_number < self.infected_number):    # Damit nur theoretisch funktionierende Simulationen in data_list gespeichert werden
            data_list[pos][2][3] = self.node_number
        else:
            data_list[pos][2][3] = self.infected_number
        data_list[pos][2][4] = self.node_speed
        data_list[pos][2][5] = self.hospital_number
        data_list[pos][2][6] = self.hospital_capacity
        data_list[pos][2][7] = self.recovery_time
        data_list[pos][2][8] = self.hospital_distance
        data_list[pos][2][9] = self.infection_radius
        data_list[pos][2][10] = self.movement_radius
        data_list[pos][2][11] = self.barriers
        data_list[pos][2][12] = self.canvas_x
        data_list[pos][2][13] = self.canvas_y
        data_list[pos][2][14] = self.resolution_x
        data_list[pos][2][15] = self.resolution_y


class output_simulationA:
    def __init__(self, name, steps, len_x, len_y, sim):
        self.name = name
        self.steps = steps
        self.len_x = len_x
        self.len_y = len_y
        self.sim = sim # Simulation

        # Fenster initialisieren
        out_fenster = Tk()
        out_fenster.title(self.name)
        out_fenster.resizable(0, 0)
        out_fenster.config(bg='white')

        # Fenstergröße
        out_fenster.geometry("600x600")

        # Frames

        grafic_frame = Frame(master=out_fenster, bg='green')
        grafic_frame.pack(padx='5', pady='5', fill=X)

        slider_frame = Frame(master=out_fenster, bg='red')
        slider_frame.pack(side='bottom', padx='5', pady='5', fill=X)

        # Grafik
        data = self.sim.images[0]

        image = data
        fig = plt.figure(figsize=(5,4))
        im = plt.imshow(image) # later use a.set_data(new_data)
        ax = plt.gca()
        ax.set_xticks([0])
        ax.set_yticks([0])
        #ax.set_xticklabels(["Hundert","Null"])
        #ax.set_yticklabels([100,100])

        plt.suptitle (self.name, fontsize=16)
        # a tk.DrawingArea
        canvas = FigureCanvasTkAgg(fig, master=grafic_frame)
        canvas.get_tk_widget().pack(fill=BOTH, expand=1)
        canvas.draw()
        plt.close()

        # Grafik-Update-Funktion: Wird aufgerufen, wenn der Slider bewegt wird
        def grafic_change(self):
            data = sim.images[int(self)]
            im.set_data(data)

            canvas.draw()

        # Reset-Button: Führt Simulation ein weiteres Mal aus
        def reset_button_action():
            sim.run()
            sim.generate_images()
            data = sim.images[0]
            time_slider.set(0)
            im.set_data(data)

            canvas.draw()

        # Komponenten

        time_slider = Scale(slider_frame, from_=0, to=self.steps-1, tickinterval=50, orient=HORIZONTAL, length=300, command=grafic_change)
        time_slider.set(0)
        time_slider.pack(side=TOP, pady=5, padx=10)


        reset_button = Button(slider_frame, text="reset", command=reset_button_action, width=15)
        reset_button.pack(side=BOTTOM, pady=5, padx=10)

        # Fenster starten
        out_fenster.mainloop()




# Funktionen der Menubar-Items

# Info-Button
def action_get_info_dialog():
    m_text = "    ************************\n    Autor: Paulo, Enzo, Bjarne, Lewis & Samuel\n    Date: 30.12.20\n    Version: 9.21\n    ************************"
    messagebox.showinfo(message=m_text, title = "Infos")

# Erstellung einer neuen Simulation des Rechteck-Formats
def create_typ_0_button_action():
    toolbox[1] += 1
    # default Werte
    data =[0,200,200,[[100,100,110,110],[10,10]],300,0.15,0.25]
    # Erstellung des Frames
    frame_simulation = input_simulationA(toolbox[1],"Untitled",data[1],data[2],data[3],data[4],data[5],data[6])
    frame_simulation.create_frame()
    # Hinzufügen der Simulation in das data_list-Array
    data_list.append([toolbox[1]]+["Untitled"]+[data]+[None]+[frame_simulation])

    id = toolbox[1]
    # Menübar hinzufügen zu Simulation-Menu
    simulation_menu.add_command(label="Untitled"+str(id), command=lambda: action_simulation(id))

    # Wenn mit dieser Simulation die Simulationsanzahl von 4 überschritten wird, d.h. 5 vorhanden sind, dann sollen die Buttons "Create" und "Load" disabled werden
    if(len(data_list) > 4):
        datei_menu.entryconfig(1, state=DISABLED)
        datei_menu.entryconfig(0, state=DISABLED)

# Erstellung einer neuen Simulation des Node-Formats
def create_typ_1_button_action():
    toolbox[1] += 1
    # default Werte
    data =[1,30, 400, 5, 30, 3, 5, 2, 300, 50, 500, [[800,100,800,800]], 1600, 900, 1600, 900]
    # Erstellung des Frames
    frame_simulation = input_simulationB(toolbox[1],"Untitled",data[1],data[2],data[3],data[4],data[5],data[6],data[7],data[8],data[9],data[10],data[11],data[12],data[13],data[14],data[15])
    frame_simulation.create_frame()
    # Hinzufügen der Simulation in das data_list-Array
    data_list.append([toolbox[1]]+["Untitled"]+[data]+[None]+[frame_simulation])

    id = toolbox[1]
    # Menübar hinzufügen zu Simulation-Menu
    simulation_menu.add_command(label="Untitled"+str(id), command=lambda: action_simulation(id))

    # Wenn mit dieser Simulation die Simulationsanzahl von 4 überschritten wird, d.h. 5 vorhanden sind, dann sollen die Buttons "Create" und "Load" disabled werden
    if(len(data_list) > 4):
        datei_menu.entryconfig(1, state=DISABLED)
        datei_menu.entryconfig(0, state=DISABLED)

# Laden einer Simulation
def load_button_action():
    # Öffnen und lesen von txt-Dateien
    filepath = askopenfilename(
        filetypes=[("Text Files", "*.txt")]
    )
    if not filepath:
        return
    with open(filepath, "r") as input_file:
        try:
            # Inhalt der Text-Datei: Zeilen als Array-Einträge nehmen
            text = input_file.read()
            text = text.split('\n')
            # Hochsetzen des Load-Counters
            toolbox[1] += 1
            
            # Wenn das Rechteck-Format bei der Simulation ausgewählt wurde
            if(int(text[1]) == 0):
                # Strings aus der Text-Datei in richtige Datentypen umwandeln
                data =[int(text[1]),int(text[2]),int(text[3]),literal_eval(text[4]),int(text[5]),float(text[6]),float(text[7])]
                # Erstellung des Frames
                frame_simulation = input_simulationA(toolbox[1],text[0],int(text[2]),int(text[3]),literal_eval(text[4]),int(text[5]),float(text[6]),float(text[7]))
                
            elif(int(text[1]) == 1):
                # Strings aus der Text-Datei in richtige Datentypen umwandeln
                data =[int(text[1]),int(text[2]),int(text[3]),int(text[4]),int(text[5]),int(text[6]),int(text[7]),int(text[8]),int(text[9]),int(text[10]),int(text[11]),literal_eval(text[12]),int(text[13]),int(text[14]),int(text[15]),int(text[16])]
                # Erstellung des Frames
                frame_simulation = input_simulationB(toolbox[1],text[0],int(text[2]),int(text[3]),int(text[4]),int(text[5]),int(text[6]),int(text[7]),int(text[8]),int(text[9]),int(text[10]),int(text[11]),literal_eval(text[12]),int(text[13]),int(text[14]),int(text[15]),int(text[16]))

            frame_simulation.create_frame()
            # Hinzufügen der Simulation in das data_list-Array
            data_list.append([toolbox[1]]+[text[0]]+[data]+[filepath]+[frame_simulation])

            id = toolbox[1]
            # Menübar hinzufügen zu Simulation-Menu
            simulation_menu.add_command(label=text[0], command=lambda: action_simulation(id))

            # Wenn mit dieser Simulation die Simulationsanzahl von 4 überschritten wird, d.h. 5 vorhanden sind, dann sollen die Buttons "Create" und "Load" disabled werden
            if(len(data_list) > 4):
                datei_menu.entryconfig(1, state=DISABLED)
                datei_menu.entryconfig(0, state=DISABLED)
        except:
            m_text = "    ************************\n    Geladene Datei ist fehlerhaft\n    ************************"
            messagebox.showinfo(message=m_text, title = "Error")

# Auswerfen der aktuell ausgewählten Simulation aus dem Editor
def dismiss_button_action():
    playsound('Soundeffects/Blop.mp3')
    # Button aus der Menubar entfernen
    simulation_menu.delete(toolbox[0])
    # Angezeigter Frame löschen
    data_list[toolbox[0]][4].frame.pack_forget()
    # Simulation aus dem data_list-Array löschen
    del data_list[toolbox[0]]

    set_simulation(-1)
    # "Create" und "Load" Button in der Menubar enablen, da auf jeden Fall das Maximum an Simulationen nicht mehr erreicht ist
    datei_menu.entryconfig(1, state=NORMAL)
    datei_menu.entryconfig(0, state=NORMAL)

# Ändert Fenster-Titel und Frames: -1 ist kein Frame ausgewählt
def set_simulation(num):
    # Zurücksetzen des aktuellen Frames, außer wenn keiner ausgewählt ist
    if(num > -1 and toolbox[0] != -1):
        data_list[toolbox[0]][4].frame.pack_forget()
    # aktualisieren der variable des aktuell ausgewählten Frames
    toolbox[0] = num
    # Wenn nicht "keine Simulation" ausgewählt wurde
    if(num > -1 and toolbox[0] != -1):
        fenster.title(data_list[num][1])
        # "Save" und "Dismiss" Button in der Menubar aktivieren
        bearbeiten_menu.entryconfig(1, state=NORMAL)
        bearbeiten_menu.entryconfig(0, state=NORMAL)
        # Frame der Simulation anzeigen
        data_list[toolbox[0]][4].frame.pack(fill=BOTH, expand=True, side=BOTTOM, anchor=S)
    # Wenn "keine Simulation" ausgewählt wurde
    else:
        fenster.title("Der Simulator-Simulator")
        # "Save" und "Dismiss" Button in der Menubar deaktivieren
        bearbeiten_menu.entryconfig(1, state=DISABLED)
        bearbeiten_menu.entryconfig(0, state=DISABLED)


# Speichern der aktuell ausgewählten Simulation
def save_button_action():
    # Wenn kein Dateipfad vorhanden ist
    if(data_list[toolbox[0]][3] == None):
        # Speicherort auswählen
        filepath = asksaveasfilename(
            defaultextension="txt",
            filetypes=[("Text Files", "*.txt")],
        )
    # Wenn bereits ein Dateipfad vorhanden ist
    else:
        filepath = data_list[toolbox[0]][3]

    if not filepath:
        return
    with open(filepath, "w") as output_file:
        # Das data_list-Array aktualisieren
        data_list[toolbox[0]][4].update_data_list()
        # data_list Informationen in richtige Form bringen
        text = data_list[toolbox[0]][1]
        for i in range(len(data_list[toolbox[0]][2])):
            text += "\n" + str(data_list[toolbox[0]][2][i])
        output_file.write(text)
        # Falls gerade erst ein Dateipfad ausgewählt wurde, soll dieser hinterlegt werden, um beim nächsten Speichern nicht die Datei neu zu speichern, sondern die Datei einfach zu updaten
        data_list[toolbox[0]][3] = str(filepath)

# Function, welche ausgeführt wird, wenn man in der Menubar eine Simulation auswählt
def action_simulation(id):
    # finden der Simulation im data-list-Array
    for i in range(len(data_list)):
        if(data_list[i][0] == id):
            pos = i
            break

    set_simulation(pos)

# Schließen des Programmes
def exit_action():
    fenster.destroy()



# Menüleiste erstellen
menuleiste = Menu(fenster)

# Menü "Datei" erstellen
datei_menu = Menu(menuleiste, tearoff=0)
# Untermenü "Create" erstellen
create_menu = Menu(datei_menu, tearoff=0)
datei_menu.add_cascade(label="Create", menu=create_menu)

# Menü "bearbeiten","help" und "simulation" erstellen
bearbeiten_menu = Menu(menuleiste, tearoff=0)
help_menu = Menu(menuleiste, tearoff=0)
simulation_menu = Menu(menuleiste, tearoff=0)

# Menü "Datei"
create_menu.add_command(label="Typ 0", command=create_typ_0_button_action)
create_menu.add_command(label="Typ 1", command=create_typ_1_button_action)
datei_menu.add_command(label="Load", command=load_button_action)
datei_menu.add_separator() # Fügt eine Trennlinie hinzu
datei_menu.add_command(label="Exit", command=exit_action)

# Menü "Bearbeiten"
bearbeiten_menu.add_command(label="Dismiss", command=dismiss_button_action, state=DISABLED)
bearbeiten_menu.add_command(label="Save", command=save_button_action, state=DISABLED)

# Menü "Help"
help_menu.add_command(label="Info", command=action_get_info_dialog)
help_menu.add_command(label="Beispiel") # noch ohne Funktion

# Menüs der Menüleiste hinzufügen
menuleiste.add_cascade(label="Datei", menu=datei_menu)
menuleiste.add_cascade(label="Bearbeiten", menu=bearbeiten_menu)
menuleiste.add_cascade(label="Help", menu=help_menu)
menuleiste.add_cascade(label="Auswahl", menu=simulation_menu)

# Die Menüleiste mit den Menüeinträgen dem Fenster übergeben
fenster.config(menu=menuleiste)


# Fenster starten
fenster.mainloop()


print(data_list) # Für Testzwecke
