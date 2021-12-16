import numpy as np
import time
from tkinter import *
from tkinter import filedialog
from PIL import ImageTk, Image
import PIL
from _thread import *

def bresenham(x1, y1, x2, y2):
    line = []
    if (x1 <= x2):  # kierunek rysowania
        xi = 1
        dx = x2 - x1
    else:
        xi = -1
        dx = x1 - x2
    if (y1 <= y2):
        yi = 1
        dy = y2 - y1
    else:
        yi = -1
        dy = y1 - y2
    x = x1
    y = y1
    line.append([int(x), int(y)])  # pierwszy punkt
    # oś OX
    if (dx >= dy):
        ai = (dy - dx) * 2
        bi = dy * 2
        d = bi - dx
        while (x != x2):
            if (d >= 0):
                x += xi
                y += yi
                d += ai
            else:
                d += bi
                x += xi
            line.append([int(x), int(y)])
    else:  # OŚ OY
        ai = (dx - dy) * 2
        bi = dx * 2
        d = bi - dy
        while (y != y2):
            if (d >= 0):
                x += xi
                y += yi
                d += ai
            else:
                d += bi
                y += yi
            line.append([int(x), int(y)])
    return line


class picture():
    input=[]
class Window(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        self.init_window()

    def init_window(self):
        self.master.title("Tomograf")
        self.pack(fill=BOTH, expand=True)

        self.inputCanvas = Canvas(self, width=300, height=300)
        self.inputCanvas.create_rectangle(2,2,300,300)
        self.inputCanvas.create_text(150,150,text="Obraz wejściowy")
        self.inputCanvas.grid(row=0,column=0)

        self.sinogramCanvas = Canvas(self, width=300,height=300)
        self.sinogramCanvas.create_rectangle(2,2,300,300)
        self.sinogramCanvas.create_text(150,150,text="Sinogram")
        self.sinogramCanvas.grid(row=0,column=1)

        self.outputCanvas = Canvas(self,width=300,height=300)
        self.outputCanvas.create_rectangle(2,2,300,300)
        self.outputCanvas.create_text(150,150,text="Obraz wyjściowy")
        self.outputCanvas.grid(row=0,column=2)

        self.uploadInputButton = Button(self,text="Import obrazu",command=self.upload_input_file, bg ="white")
        self.uploadInputButton.grid(row=1,column=0)

        xpad=5
        Label(self,text="Parametry:").grid(row=1,column=1)
        Label(self,text="Liczba detektorów:").grid(row=2,column=1,sticky='w',padx=xpad)
        self.detectorsEntry=Entry(self,width=8)
        self.detectorsEntry.grid(row=2,column=1,sticky='e',padx=xpad)

        Label(self,text="Kąt przesunięcia:").grid(row=3,column=1,sticky='w',padx=xpad)
        self.angleEntry = Entry(self,width=8)
        self.angleEntry.grid(row=3,column=1,sticky='e',padx=xpad)

        Label(self,text="Rozwartość:").grid(row=4,column=1,sticky='w',padx=xpad)
        self.coneSpanEntry=Entry(self,width=8)
        self.coneSpanEntry.grid(row=4,column=1,sticky='e',padx=xpad)

        self.stepsVar = IntVar(value=1)
        stepsCheckbutton = Checkbutton(self,text="Widoczne kroki pośrednie",variable=self.stepsVar)
        stepsCheckbutton.grid(row=2,column=2,columnspan=2)

        self.speedLabel = Label(self,text="Prędkość:")
        self.speedLabel.grid(row=3,column=2,columnspan=2)
        self.speedSlider = Scale(self,from_=1,to=100,orient=HORIZONTAL,length=200)
        self.speedSlider.grid(row=4,column=2,columnspan=2,rowspan=2)

        self.startButton = Button(self,text="Start",command=self._makeSinogram, width=20, height=2, bg='lightblue')
        self.startButton.grid(row=3,column=0,sticky='n',padx=20,pady=10)

        self.set_default_values()
        self.master.update()

    def set_default_values(self):
        self.speedSlider.set(100)
        self.detectorsEntry.insert(END,50)
        self.angleEntry.insert(END,5)
        self.coneSpanEntry.insert(END,90)

    def upload_input_file(self):
        filename = filedialog.askopenfilename()
        self.set_input_image(filename)

    def set_image(self,path,canvas):
        img = Image.open(path)
        print(img)
        temp = np.array(img.convert('L')) #blackscreen
        img = img.resize((canvas.winfo_width(), canvas.winfo_height()), Image.ANTIALIAS)
        picture.input = temp
        canvas.image = ImageTk.PhotoImage(img)
        canvas.create_image(0, 0, image=canvas.image, anchor=NW)

    def set_input_image(self,path):
        self.set_image(path,self.inputCanvas)

    def set_sinogram_image(self,path):
        self.set_image(path,self.sinogramCanvas)

    def set_output_image(self,path):
        self.set_image(path,self.outputCanvas)

    def _makeSinogram(self):
        self.sinogramCanvas.create_rectangle(0, 0, self.sinogramCanvas.winfo_width(), self.sinogramCanvas.winfo_height(), fill="black")
        start_new_thread(self.makeSinogram, ())

    def makeSinogram(self):
        pic = picture.input
        nDet = int(self.detectorsEntry.get())
        alpha = float(self.angleEntry.get())
        span = float(self.coneSpanEntry.get())
        spanRad = span * np.pi / 180;
        r = len(pic[0])
        lines = []
        i = 0
        sinogram=[[0 for x in range(nDet)] for y in range(int(360/alpha))]
        while i < 360:
            lines.append([])
            angleRad = i * np.pi / 180
            xe = r * np.cos(angleRad)
            ye = r * np.sin(angleRad)
            xe = int(xe) + np.floor(r / 2)
            ye = int(ye) + np.floor(r / 2)

            for d in range(0, nDet):
                xd = r * np.cos(angleRad + np.pi - spanRad / 2 + d * (spanRad / (nDet - 1)))
                yd = r * np.sin(angleRad + np.pi - spanRad / 2 + d * (spanRad / (nDet - 1)))
                xd = int(xd) + np.floor(r / 2)
                yd = int(yd) + np.floor(r / 2)

                line = bresenham(xe, ye, xd, yd)
                pixel = np.float(0)
                counter = int(0)
                for [x, y] in line:
                    if x >= 0 and y >= 0 and x < r and y < r:
                        pixel += float(pic[x, y])
                        counter += 1
                if counter > 0:
                    sinogram[int(i/alpha)][d]=(pixel / counter)
                else:
                    sinogram[int(i/alpha)][d]=0
                lines[-1].append([xe, ye, xd, yd])
            i += alpha
            time.sleep((100-self.speedSlider.get())/1000)
            if self.stepsVar.get() == 1:
                self.setSinogramOutput(sinogram)
        self.setSinogramOutput(sinogram)
        start_new_thread(self.makeOutputPicture, (sinogram,lines,pic))
        return sinogram, lines

    def setSinogramOutput(self,sin):
        self.sinogramCanvas.image = ImageTk.PhotoImage(PIL.Image.fromarray(np.array(sin)).resize((self.sinogramCanvas.winfo_width(),self.sinogramCanvas.winfo_height()),Image.ANTIALIAS))
        self.sinogramCanvas.create_image(0, 0, image=self.sinogramCanvas.image, anchor=NW)

    def setOutputPicture(self,pic):
        self.outputCanvas.image = ImageTk.PhotoImage(PIL.Image.fromarray(np.array(pic)).resize((self.outputCanvas.winfo_width(),self.outputCanvas.winfo_height()),Image.ANTIALIAS))
        self.outputCanvas.create_image(0, 0, image=self.outputCanvas.image, anchor=NW)

    def makeOutputPicture(self, sinogram, lines, pic):
        self.outputCanvas.create_rectangle(0, 0, self.outputCanvas.winfo_width(), self.outputCanvas.winfo_height(), fill="black")
        OutPic = np.zeros([np.shape(pic)[0], np.shape(pic)[1]])
        OutPicsums = np.zeros([np.shape(pic)[0],np.shape(pic)[1]])
        sx = np.shape(sinogram)[0]
        sy = np.shape(sinogram)[1]
        counter = np.zeros([np.shape(pic)[0], np.shape(pic)[1]])
        for i in range(0, sx):
            for j in range(0, sy):
                x0, y0, x1, y1 = lines[i][j]
                line = bresenham(x0, y0, x1, y1)
                for [x, y] in line:
                    if x >= 0 and y >= 0 and x < np.shape(pic)[0] and y < np.shape(pic)[1]:
                        OutPicsums[x][y]+=sinogram[i][j]
                        counter[x][y]+=1
                        OutPic[x][y]=OutPicsums[x][y]/counter[x][y]
            time.sleep((100-self.speedSlider.get())/1000)
            if self.stepsVar.get()==1:
                self.setOutputPicture(OutPic)
        self.setOutputPicture(OutPic)
        return OutPic

root = Tk()
root.geometry("950x460")
app=Window(root)
root.mainloop()
