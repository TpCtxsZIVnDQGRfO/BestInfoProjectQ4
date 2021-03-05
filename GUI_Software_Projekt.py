#!/usr/bin/env python
# coding: utf-8

from tkinter import *
from tkinter import messagebox
from tkinter.filedialog import askopenfilename, asksaveasfilename
from Zellulare_Automaten_Simulation import *
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
        data = self.sim.get(0)

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
            data = sim.get(int(self))
            im.set_data(data)

            canvas.draw()

        # Reset-Button: Führt Simulation ein weiteres Mal aus
        def reset_button_action():
            sim.run()
            data = sim.get(0)
            time_slider.set(0)
            im.set_data(data)

            canvas.draw()

        # Komponenten

        time_slider = Scale(slider_frame, from_=0, to=self.steps ,tickinterval=50, orient=HORIZONTAL, length=300, command=grafic_change)
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
    print("Noch in Bearbeitung")

# Laden einer Simulation
def load_button_action():
    # Öffnen und lesen von txt-Dateien
    filepath = askopenfilename(
        filetypes=[("Text Files", "*.txt")]
    )
    if not filepath:
        return
    with open(filepath, "r") as input_file:
        # Inhalt der Text-Datei: Zeilen als Array-Einträge nehmen
        text = input_file.read()
        text = text.split('\n')
        # Hochsetzen des Load-Counters
        toolbox[1] += 1
        # Strings aus der Text-Datei in richtige Datentypen umwandeln
        data =[int(text[1]),int(text[2]),int(text[3]),literal_eval(text[4]),int(text[5]),float(text[6]),float(text[7])]
        # Wenn das Rechteck-Format bei der Simulation ausgewählt wurde
        if(data[0] == 0):
            # Erstellung des Frames
            frame_simulation = input_simulationA(toolbox[1],text[0],int(text[2]),int(text[3]),literal_eval(text[4]),int(text[5]),float(text[6]),float(text[7]))
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

# Auswerfen der aktuell ausgewählten Simulation aus dem Editor
def dismiss_button_action():
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
