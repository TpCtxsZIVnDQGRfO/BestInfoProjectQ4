import numpy as np
import matplotlib.pyplot as plt
import random
import math
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import cv2
import glob
import os
from os.path import isfile, join

import shutil
from sympy import Point, Line, Segment
from tqdm import tqdm

class Simulation:
    
    def __init__(self,Knotenliste, flowchart, nodeRadius, videoLength, fps, speed=5):
        self.nodes = Knotenliste #Liste von Knotenobjekten
        #Umwandlung der Matrix in eine Liste(vielleicht nicht sinnvoll)
        self.flowchart = flowchart #Numpyarray für die Zustände und Zustandsübergangswahrscheinlichkeit
        self.flow  = [] #versteht nur Paulo ganz
        self.canvas = [100,100] #Größe  der Fläche
        self.resolution = self.canvas
        self.nodeRadius = nodeRadius #Radius  der Nodepunkte
        self.colours = ["green","red","blue"] #Farben der Nodepunkte in Reihenfolge
        self.links = [] #[Node1,Node2,distance]
        self.speed = speed/fps #bin mir nicht sicher, ob das /fps richtig ist
        self.fps = fps
        self.length = videoLength #in Sekunden
        self.frames = videoLength * fps #Anzahl der Frames
        self.coordList = [] #später benötigt, um Dopplung von Startkoordinaten zu vermeiden (ist das so wichtig?)
        self.barriers = [] #[[[Xstart1,Ystart1],[Xende1,Yende1]],[[Xstart2,Ystart2],[Xende2,Yende2]],...]
        self.maxDist = 20
        self.movementRadius = None
        self.barrierColour = "red"
        self.barrierWidth = 2
        self.connecColour = "white"
        self.connecWidth = 1

        
        shutil.rmtree('pix\\')#leerer Ordner, in dem die einzelnen Frames gespeichert werden
        newpath = 'pix\\' #Edgecase: löscht momentan noch Inhalt von Ordnern, die schon existieren und so heißen
        if not os.path.exists(newpath):
            os.makedirs(newpath)
        for i in range(flowchart.shape[0]): #shape ist die Größe (-> [0] Länge in x-Richtung)
            for j in range(flowchart.shape[1]):
                if flowchart[i,j] != 0:
                    self.flow.append([i,j,flowchart[i,j]*5/self.fps]) #Wahrscheinlichkeiten an Zeit und nicht an Frames/Zeitschritte gebunden
        #print(self.flow)            

    def addRandomNode(self,amount,state): #erstellt x neue Nodes an zufälligen Koordinaten
        for i in range(amount):
            check = False 
            while check == False:
                k = [random.randint(0,self.canvas[0]),random.randint(0,self.canvas[1])]
                if k  not in self.coordList:
                    self.coordList.append(k)
                    check = True

            if self.nodes == []:
                id = 0
            else:
                id = self.nodes[-1].ID+1
            self.nodes.append(Knoten(id,k,state,[],None))

    def distance(self,Knoten1, Knoten2): #berechnet den Abstand der beiden Knoten
        return math.sqrt((Knoten1.k[0]-Knoten2.k[0])**2+(Knoten1.k[1]-Knoten2.k[1])**2)
    
    def generate_connections(self): #aktualisiert die Verbindungsdaten in den Nodes
        self.links = []
        for i in range(len(self.nodes)):
            self.nodes[i].connec = []
        for i in range(len(self.nodes)):
            for j in range(len(self.nodes)-i):
                wegVersperrt = False
                distance = self.distance(self.nodes[i],self.nodes[j+i])
                for barrier in self.barriers:
                    if wegVersperrt == False:
                        #print(j)
                        k1 = sim.nodes[i].k
                        k2 = sim.nodes[i+j].k
                        b1 = barrier[0]
                        b2 = barrier[1]
                        if Utility.do_they_intersect(k1, k2, b1, b2): #schneiden sich Barrierenstrecke und Verbindungsstrecke?
                            wegVersperrt = True
                if distance < self.maxDist and wegVersperrt == False:
                    self.nodes[i].connec.append([self.nodes[j+i],distance])
                    self.nodes[j+i].connec.append([self.nodes[i],distance])
                    self.links.append([self.nodes[j+i],self.nodes[i],distance]) #damit wir sie in visualLinks einfach durchgehen können
        #print(self.links)
                    
    def visualLinks(self): #malt nur die Verbindungslinien auf einen leeren grauen Canvas
        r = self.nodeRadius
        dis = [self.resolution[0]/self.canvas[0],self.resolution[1]/self.canvas[1]] #distortion
        image = Image.new('RGB', (round((self.canvas[0]+2*r)*dis[0]),round((self.canvas[1]+2*r)*dis[1])),color = (41, 49, 51)) #Anthrazit
        #image = Image.open("gradient-grey-wallpaper.jpg")
        #image.thumbnail((round((self.canvas[0]+2*r)*dis[0]),round((self.canvas[1]+2*r)*dis[1])))
        fill = self.connecColour
        width = self.connecWidth 
        draw = ImageDraw.Draw(image)
        for link in self.links:
            draw.line((((link[0].k[0]+r)*dis[0], (link[0].k[1]+r)*dis[1]), ((link[1].k[0]+r)*dis[0], (link[1].k[1]+r)*dis[1])), fill=fill,width=width)
        return image

    def visualBarriers(self, background): #malt auf das gegebene Bild die Barrierenlinien
        r = self.nodeRadius
        dis = [self.resolution[0]/self.canvas[0],self.resolution[1]/self.canvas[1]] #distortion
        draw = ImageDraw.Draw(background)
        fill = self.barrierColour = "red"
        width = self.barrierWidth
        for barrier in self.barriers:
            draw.line((((barrier[0][0]+r)*dis[0], (barrier[0][1]+r)*dis[1]), ((barrier[1][0]+r)*dis[0], (barrier[1][1]+r)*dis[1])), fill=fill,width=width)
        return background

    def visualNodes(self, background): #malt auf das gegebene Bild die Nodepunkte
        r = self.nodeRadius
        dis = [self.resolution[0]/self.canvas[0],self.resolution[1]/self.canvas[1]] #distortion
        image = background
        draw = ImageDraw.Draw(image) #Note: damit die Punkte vollständig auf das Bild passen, ist das Bild noch an den Rändern um r länger und alles verschoben
        for node in self.nodes:
            k = node.k               #Außerdem: der Ursprung ist oben links
            for i in range(3):
                if node.state[i] == 1:
                    c = self.colours[i]
            draw.ellipse(((k[0]+r)*dis[0]-r, (k[1]+r)*dis[1]-r, (k[0]+r)*dis[0]+r, (k[1]+r)*dis[1]+r), fill = c, outline =c) #https://stackoverflow.com/questions/20747345/python-pil-draw-circle#20747513
        #image = image.crop((0,0,round((self.canvas[0]+2*r)*dis[0]),round((self.canvas[1]+2*r)*dis[1])))
        return image

    def visualComplete(self): #erstellt das ganze Bild mit allen Teilen
        return self.visualNodes(self.visualBarriers(self.visualLinks()))
        
    def run(self,steps): #die eigentliche Simulation;

#########
        #der Flow wird steps-mal auf den derzeitigen Zustand angewandt
#########

        for i in range(steps):
            tempI = []
            tempR = []
            if self.movementRadius != 0:
                self.generate_connections()
            #print("lololololol")
            for j in range(len(self.nodes)):
                if self.nodes[j].state == [0,1,0]:
                    for k in range(len(self.nodes[j].connec)):
                        if self.nodes[j].connec[k][0].state == [1,0,0]:
                            if random.random()<self.flow[0][2]:
                                tempI.append(self.nodes[j].connec[k][0])
                        if random.random()<self.flow[1][2]:
                            tempR.append(self.nodes[j])
            for j in tempI:
                j.state = [0,1,0]
            for j in tempR:
                j.state = [0,0,1]

#############
            #im folgenden Teil werden die Nodes bewegt
#############
            if self.movementRadius != 0:
                for j in range(len(self.nodes)):
                    node = self.nodes[j]
                    norm = math.sqrt(node.moveVec[0]**2+node.moveVec[1]**2)
                    node.moveVec = [node.moveVec[0]/norm,node.moveVec[1]/norm] #Bewegungsvektor normieren
                    if node.beugungsRate == 0:                          #bei Fragen zu diesem ganzen Beugungszeug einfach Bjarne fragen
                        node.beugungsRate = random.randint(5,20)        #keine Lust, das jetzt zu erklären
                        node.modVec = [-node.moveVec[1],node.moveVec[0]] #Modifizierungsvektor steht senkrecht auf dem Bewegungsvektor
                    node.moveVec = [node.moveVec[0]+node.modVec[0]/20*node.beugungsRate,node.moveVec[1]+node.modVec[1]/20*node.beugungsRate]
                    fuCoords = [node.k[0]+node.moveVec[0]/10*self.speed,node.k[1]+node.moveVec[1]/10*self.speed] #die Koordinaten, an denen die Node als nächtes wäre
                    wegVersperrt = False
                    for barrier in self.barriers:
                        k1 = node.k
                        k2 = fuCoords
                        b1 = barrier[0]
                        b2 = barrier[1]
                        if Utility.do_they_intersect(k1, k2, b1, b2): #prüfen, ob die geplante Bewegungstrecke mit einer Barriere kollidiert
                            wegVersperrt = True
                    nichtZuWeitWeg = False
                    if self.movementRadius != None:
                        if Utility.coordDistance(fuCoords,node.startKoord) <= self.movementRadius:
                            nichtZuWeitWeg = True
                    if 0 <= fuCoords[0] <= self.canvas[0] and 0 <= fuCoords[1] <= self.canvas[1] and not wegVersperrt and nichtZuWeitWeg: 
                        node.k = fuCoords #bewegen, wenn der Weg frei ist und nicht aus dem Bild raus führt (sonst stehen bleiben)
                    node.beugungsRate -= 1
                    node.moveVec = [node.moveVec[0]+node.modVec[0]/20,node.moveVec[1]+node.modVec[1]/20] #die Krümmung wird geringer

                        
class Knoten():

    def __init__(self,ID,Koordinaten, Zustand, Verbindungen, Bedingungen):
        self.ID = ID #ID ist int (bisher nutzlos)
        self.k = Koordinaten #Koordinaten [Xfloat,Yfloat]
        self.startKoord = Koordinaten #für Bewegungsradius
        self.state = Zustand #suscepteble, infective, recovered als array: [0,0,1]
        self.connec = Verbindungen #momentan [[Knoten, Distanz als int], [usw]]
        self.condit = Bedingungen #bisher nichts
        theta = (2.0 * math.pi) * random.random() 
        self.moveVec = [math.cos(theta),math.sin(theta)] #erster Bewegungsvektor ist Randompunkt auf Einheitskreis
        self.modVec = [0,0] #der Modifizierungsvektor wird in run() bestimmt
        self.beugungsRate = 0

    def distance(self,Knoten): #berechnet den Abstand zu diesem Knoten
        return math.sqrt((self.k[0]-Knoten.k[0])**2+(self.k[1]-Knoten.k[1])**2)

    def actual_connect(self, max_distance = 50): #aktualisiert die Verbindungsdaten dieser Node
        self.connec = []
        for i in range(len(Knotenliste)):
            distance = self.distance(Knotenliste[i])
            if distance < max_distance:
                self.connec.append([Knotenliste[i], distance])

class Utility(): #allerlei nützliche Funktionen

    #braucht scheinbar keine __init__()
        
    def cptv(pathIn, pathOut, fps): #convert_pictures_to_video (nimmt alle Videos an gegebenem Pfad und hängt sie zum Video aneinander)
        frame_array=[]
        files= [f for f in os.listdir(pathIn)if isfile(join(pathIn,f))]
        for i in range(len(files)):
            filename=pathIn+files[i]
            img=cv2.imread(filename)
            height, width, layers = img.shape
            size = (width,height)

            frame_array.append(img)
        out=cv2.VideoWriter(pathOut,cv2.VideoWriter_fourcc(*'DIVX'), fps,size)
        for i in range(len(frame_array)):
            out.write(frame_array[i]) #aus Youtubevideo
        out.release()

    #Leider halt für GERADEN
    def line_intersection(line1, line2): #beides Zweierlisten von Tupeln
        xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
        ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1]) #MERKE: "line" = "Gerade" und "(line) segment" = "strecke"

        def det(a, b):
            return a[0] * b[1] - a[1] * b[0]

        div = det(xdiff, ydiff)
        if div == 0:
           return False #kein Schnittpunkt

        d = (det(*line1), det(*line2))
        x = det(d, xdiff) / div
        y = det(d, ydiff) / div
        return True #Schnittpunkt

    def do_they_intersect( p0, p1, p2, p3 ): #ja, das ist von StackOverflow geklaut, aber psssst
        s10_x = p1[0] - p0[0]
        s10_y = p1[1] - p0[1]
        s32_x = p3[0] - p2[0]
        s32_y = p3[1] - p2[1]

        denom = s10_x * s32_y - s32_x * s10_y 
        if denom == 0:
            return False # collinear
        denom_is_positive = denom > 0
        s02_x = p0[0] - p2[0]
        s02_y = p0[1] - p2[1]
        s_numer = s10_x * s02_y - s10_y * s02_x
        if (s_numer < 0) == denom_is_positive:
            return False # no collision
        t_numer = s32_x * s02_y - s32_y * s02_x

        if (t_numer < 0) == denom_is_positive:
            return False # no collision
        if (s_numer > denom) == denom_is_positive or (t_numer > denom) == denom_is_positive:
            return False # no collision


        return True #collision

    def coordDistance(a, b):
        return math.sqrt((a[0]-b[0])**2+(a[1]-b[1])**2)
            
    


#----------------------------Beispielinitialisierung Zufälliges Netz SIR---------------------------------------------

#In dieser Beispielinitialisierung wird ein zufälliges Netz generiert und jeder Knoten repräsentiert eine Person und
#Verbindungen zwischen Knoten regelmäßigen Kontakt zwischen den Personen, jede Verbindung hat einen Wert von 0 bis 1,
#welcher für die Übertragungswahrscheinlichkeit zwsichen den Personen steht
#Wie im Zellulären Automatenmodell gibt es drei Zustände: suscepteble, infective, recovered (siehe Zelluläler-Automat-Simulation)

flowchart = np.array([[0,0.05,0],[0,0,0.00025],[0,0,0]])
sim = Simulation([],flowchart, 5, 10, 6, 90)
sim.frames = 1000
sim.canvas = [1600,900]
sim.resolution = [1600,900]
sim.addRandomNode(400,[1,0,0])
sim.maxDist = 50
sim.movementRadius = 500

sim.barrierColour = "red"
sim.barrierWidth = 2
sim.connecColour = "white"
sim.connecWidth = 1

sim.barriers.append([[800,100],[800,800]])

for i in range(1):
    sim.nodes[i].state = [0,1,0] #die ersten fünf Nodes sind infiziert

#frameArr = []
#anzeige = tqdm(total=sim.frames,position=0,leave=False)
for i in range(sim.frames):
    sim.run(1)
    #frameArr.append(sim.visualComplete())
    sim.visualComplete().save("pix\\"+"0"*(5-len(str(i)))+str(i)+".jpeg", 'JPEG', ppcm=[100,100], quality=100)
    print(i)
    #anzeige.set_description("Loading...".format(i))
    #anzeige.update(1)
    
Utility.cptv("pix\\", "video.mp4", sim.fps)
print("Das Video wurde erstellt.")      #██████████████████████████████████████████████████████████ bestes Zeichen 
