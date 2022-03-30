import os
from tkinter import *
from tkinter.filedialog import askdirectory
import tkinter.messagebox
from ProcessImage import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import ImageTk, Image
import matplotlib.pyplot as plt
from matplotlib import ticker

class ViewMain:
    def __init__(self):
        '''
        Initialize the main window of detection
        '''
        self.viewmain = Tk()
        self.viewmain.title('Segmentation')
        self.viewmain.geometry("500x550")

        self.no_item = 0

        self.Imgs = []
        self.img_current = None
        self.imgs_all = []

        self.area_total = 0
        self.area_mean = 0
        self.area_std = 0
        self.dia_mean = 0
        self.dia_std = 0
        self.ratio = 0


        self.photo = None
        self.width = 1000
        self.min_area = 0.5

        self.main_menu = Menu(self.viewmain)

        self.filemenu = Menu(self.main_menu, tearoff=False)
        self.filemenu.add_command(label="Import", command=self.ImportImage)
        self.filemenu.add_command(label="ExportCurrentImage", command=self.exportCurrentImage)
        self.filemenu.add_command(label="ExportAllImages", command=self.exportAllImages)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=self.viewmain.quit)

        self.drawmenu = Menu(self.main_menu, tearoff=False)
        self.drawmenu.add_command(label="ProcessCurrentImage", command=self.processCurrentImage)
        self.drawmenu.add_command(label="ProcessAllImages", command=self.processAllImages)
        self.drawmenu.add_command(label="DrawHistOfDias", command=self.DrawDia)
        self.drawmenu.add_command(label="DrawHistOfArea", command=self.DrawArea)


        self.main_menu.add_cascade(label="File", menu=self.filemenu)
        self.viewmain.config(menu=self.main_menu)

        self.main_menu.add_cascade(label="Process", menu=self.drawmenu)
        self.viewmain.config(menu=self.main_menu)

        self.canvas = Canvas(self.viewmain, width=400, height=400,bg = 'white')

        self.b_previous = Button(self.viewmain, text='<<<<', command=self.call_previous)
        self.b_process = Button(self.viewmain, text='Process', command=self.processCurrentImage)
        self.b_next = Button(self.viewmain, text='>>>>', command=self.call_next)


        self.b_export = Button(self.viewmain, text='Export', command=self.exportCurrentImage)

        self.t_width  = Label(self.viewmain,text = "Input the width of image(um):")
        self.e_width  = Entry(self.viewmain, width=10)


        self.title = StringVar()
        self.l_title = Label(self.viewmain,textvariable = self.title)

        self.t_minarea = Label(self.viewmain,text = "Input the minimum area of particle(um²):")
        self.e_minarea = Entry(self.viewmain, width=10)

        self.t_width .place(x=50,y=10)
        self.e_width .place(x=390,y=10, width=60, height=20)
        self.e_width .insert(0,self.width)

        self.t_minarea.place(x=50,y = 30)
        self.e_minarea.place(x=390,y = 30,width=60, height=20)
        self.e_minarea.insert(0,self.min_area)

        self.l_title.place(x=200,y=50)

        self.b_previous.place(x=50,y=490, width=60, height=30)
        self.b_process.place(x=163,y=490, width=60, height=30)
        self.b_export.place(x=276,y=490, width=60, height=30)
        self.b_next.place(x=390,y=490, width=60, height=30)

        self.viewmain.mainloop()


    def directoryBox(self,root, title=None, dirName=None):
        options = {}
        options['initialdir'] = dirName
        options['title'] = title
        options['mustexist'] = True
        root.update()
        repName = askdirectory(**options)
        return repName

    def ImportImage(self):
        '''
        Import the images in the directory
        '''
        self.Imgs = []
        while len(self.Imgs) == 0:
            rep = os.getcwd()
            rep = self.directoryBox(self.viewmain, title='Choose the folder contains the images', dirName=rep)
            if len(rep) == 0:
                rep = os.getcwd()
            os.chdir(rep)
            for element in os.listdir(rep):
                if element.endswith('.tif'):
                    namef = os.path.splitext(element)
                    self.Imgs.append(element)
        if len(self.Imgs) > 0:
            self.DisplayItem()

    def processCurrentImage(self,threshold = 25):
        '''
        Process current image, binarizer and  calculate the features
        :param threshold: the threshold to achieve binarisation
        :return:
        '''
        if len(self.Imgs) == 0:
            tkinter.messagebox.showwarning("Error", "Choose an image first")
        else:
            self.width = float(self.e_width .get())
            self.min_area = float(self.e_minarea.get())
            self.img_current = ProcessImage(self.Imgs[self.no_item])
            #We can change this variable to set the threshold, default 25
            self.img_current.process(threshold)
            self.img_current.extract(width=self.width ,min_area=self.min_area)
            self.img_current.calculateFeatures()
            tkinter.messagebox.showinfo("Finished","Process Current Image Finished")



    def processAllImages(self,threshold = 25):
        '''
        Process all images in current directory
        '''
        if len(self.Imgs) == 0:
            tkinter.messagebox.showwarning("Error", "Choose images first")
        else:
            self.width = float(self.e_width.get())
            self.min_area = float(self.e_minarea.get())
            for i in range(len(self.Imgs)):
                img = ProcessImage(self.Imgs[i])
                img.process(threshold)
                img.extract(width=self.width,min_area=self.min_area)
                img.calculateFeatures()
                self.imgs_all.append(img)
            tkinter.messagebox.showinfo("Finished","Process All Images Finished")


    def exportCurrentImage(self):
        '''
        Export the information of current image to the file csv with the name of current image
        '''
        if self.img_current == None:
            tkinter.messagebox.showwarning("Error", "Process an image first")
        else:
            self.img_current.export('Particles of {}.csv'.format(self.Imgs[self.no_item].split('.')[0]))
            tkinter.messagebox.showinfo("Finished", "Export Current Image Finished")

    def exportAllImages(self):
        '''
        Export the information of all images to the file csv with the name of current image
        '''
        if self.imgs_all == []:
            tkinter.messagebox.showwarning("Error", "Process images first")
        else:
            areas = []
            dias = []
            for img in self.imgs_all:
                self.area_total += img.total_area
                areas+=img.areas
                dias += img.dias
                self.ratio += img.ratio_area

            self.area_mean = np.mean(areas)
            self.area_std = np.std(areas)
            self.dia_mean = np.mean(dias)
            self.dia_std = np.std(dias)
            self.ratio /= len(self.imgs_all)

            with open("ResultsOfAllImages.csv", 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Total Area', 'Average Area', 'Std of Area', 'Average Diameter', 'Std of Diameter',
                                 'Ratio of particles'])
                writer.writerow([self.area_total,self.area_mean,self.area_std,self.dia_mean,self.dia_std,self.ratio])
                for img,i in zip(self.imgs_all,range(len(self.imgs_all))):
                    writer.writerow(["The {} image:".format(i)])
                    writer.writerow(['No.', 'Area', 'Diameter', 'Location'])
                    for raw_data in img.particle_list:
                        writer.writerow(raw_data)
            tkinter.messagebox.showinfo("Finished", "Export All Images Finished")


    def call_previous(self):
        '''
        Display the previous image in the directory
        '''
        if self.no_item > 0:
            self.no_item -= 1
            self.DisplayItem()

    def call_next(self):
        '''
        Display the next image in the directory
        '''
        if self.no_item < len(self.Imgs) - 1:
            self.no_item += 1
            self.DisplayItem()

    def DisplayItem(self):
        '''
        Display the current image in the directory
        '''
        img = Image.open(self.Imgs[self.no_item])
        self.title.set(self.Imgs[self.no_item].split('.')[0])
        self.l_title.place(x=200,y=50)

        basewidth = 400
        wpercent = (basewidth / float(img.size[0]))
        hsize = int((float(img.size[1]) * float(wpercent)))
        img = img.resize((basewidth, hsize), Image.ANTIALIAS)
        if (hsize > 400):
            baseh = 400
            wpercent = (baseh / float(img.size[1]))
            wsize = int((float(img.size[0]) * float(wpercent)))
            img = img.resize((wsize, baseh), Image.ANTIALIAS)
        self.photo = ImageTk.PhotoImage(img)
        self.canvas.create_image(200, 200, image=self.photo)
        self.canvas.place(x=50, y=70, width=400, height=400)

    def DrawDia(self):
        '''
        Draw the histogram of diameter of current image in a new window
        '''
        if self.img_current == None:
            tkinter.messagebox.showwarning("Error", "Process an image first")
        else:
            self.viewhistdia = Toplevel()
            self.viewhistdia.title('Hist Of Diameter '+ self.Imgs[self.no_item].split('.')[0])
            self.viewhistdia.geometry("900x600")

            min_dia = round(self.img_current.range_size[0],2)
            l_min_dia = Label(self.viewhistdia,text = "Input the minimum diameter: {:.2f}um".format(min_dia))
            e_min_dia = Entry(self.viewhistdia, width=10)

            max_dia = round(self.img_current.range_size[1],2)
            l_max_dia = Label(self.viewhistdia,text = "Input the maximum diameter: {:.2f}um".format(max_dia))
            e_max_dia = Entry(self.viewhistdia, width=10)

            l_interval = Label(self.viewhistdia,text = "Input the interval(um):")
            e_interval = Entry(self.viewhistdia, width=10)

            b_draw = Button(self.viewhistdia,text="Draw", command=lambda: self.DrawHist(self.img_current.dias,e_max_dia.get(),e_min_dia.get(),e_interval.get(), "Diameter"))

            l_min_dia.place(x=150,y=10)
            e_min_dia.place(x=450,y=10, width=60, height=20)
            e_min_dia.insert(0,min_dia)

            l_max_dia.place(x=150,y=30)
            e_max_dia.place(x=450,y=30, width=60, height=20)
            e_max_dia.insert(0,max_dia)

            l_interval.place(x=150,y = 50)
            e_interval.place(x=450,y = 50,width=60, height=20)
            e_interval.insert(0,0.5)

            b_draw.place(x = 550,y = 30,  width=60, height=20)

            self.viewhistdia.mainloop()

    def DrawArea(self):
        '''
        Draw the histogram of diameter of current image in a new window
        '''
        if self.img_current == None:
            tkinter.messagebox.showwarning("Error", "Process an image first")
        else:
            self.viewhistarea = Toplevel()
            self.viewhistarea.title('Hist Of Area '+ self.Imgs[self.no_item].split('.')[0])
            self.viewhistarea.geometry("900x1000")

            min_area = round(self.img_current.range_size[2],2)
            l_min_area = Label(self.viewhistarea,text = "Input the minimum area:{:.2f}um²".format(min_area))
            e_min_area = Entry(self.viewhistarea, width=10)

            max_area = round(self.img_current.range_size[3], 2)
            l_max_area = Label(self.viewhistarea,text = "Input the maximum area:{:.2f}um²".format(max_area))
            e_max_area = Entry(self.viewhistarea, width=10)

            l_interval = Label(self.viewhistarea,text = "Input the interval:(um²)")
            e_interval = Entry(self.viewhistarea, width=10)

            b_draw = Button(self.viewhistarea,text="Draw", command=lambda: self.DrawHist(self.img_current.dias,e_max_area.get(),e_min_area.get(),e_interval.get(), "Area"))

            l_min_area.place(x=150,y=10)
            e_min_area.place(x=450,y=10, width=60, height=20)
            e_min_area.insert(0,min_area)

            l_max_area.place(x=150,y=30)
            e_max_area.place(x=450,y=30, width=60, height=20)
            e_max_area.insert(0,max_area)

            l_interval.place(x=150,y = 50)
            e_interval.place(x=450,y = 50,width=60, height=20)
            e_interval.insert(0,0.5)

            b_draw.place(x = 550,y = 30,  width=60, height=20)

            self.viewhistarea.mainloop()

    def to_percent(self,temp):
        return '%1.0f' % (100 * temp) + '%'

    def DrawHist(self,list,num_max,num_min,interval,Type):
        '''
        The function of draw histogram
        :param list: the list of input data
        :param num_max: the minimum size of x axis
        :param num_min: the maximum size of x axis
        :param interval: the interval between the range of size
        :param Type: The type of histogram,"Diameter" or "Area"
        :return:
        '''
        f = plt.figure(figsize=(8, 10))
        ax = plt.subplot(2,2,1)
        if float(interval) != 0:
            nb_bins = int(( float(num_max) - float(num_min)) / float(interval))
        else:
            tkinter.messagebox.showerror("Error", "Interval can't be 0")
        list_in_range = []
        for i in list:
            if i > float(num_min) and i < float(num_max):
                list_in_range.append(i)

        a1,a2,a3 = plt.hist(list_in_range, nb_bins)
        plt.xlabel(Type).set_fontsize(6)
        plt.ylabel("Number").set_fontsize(6)
        plt.title("Distribution histogram").set_fontsize(6)

        ax1 = plt.subplot(2,2,2)
        ax1.set_ylim(0,sum(a1))
        ax2 = plt.twinx()
        ax1.set_ylabel("Number").set_fontsize(6)
        ax2.yaxis.set_major_formatter(ticker.PercentFormatter(xmax=len(list), decimals=0))
        ax2.set_ylabel("Percent").set_fontsize(6)
        for i in range(1,len(a1)):
            a1[i] = a1[i] + a1[i-1]
        plt.bar(a2[:-1],a1,width = 4)
        plt.plot(a2[:-1], a1)
        ax1.set_xlabel(Type).set_fontsize(6)
        plt.title("Cumulative distribution histogram").set_fontsize(6)



        f3 = plt.subplot(2, 2, 3)
        plt.hist(list_in_range, nb_bins,density = True)
        f3.set_xscale('log')
        plt.xlabel(Type).set_fontsize(6)
        plt.ylabel("Percent of Numbers").set_fontsize(6)
        plt.title("Distribution histogram").set_fontsize(6)


        f4 = plt.subplot(2, 2, 4)

        y = np.divide(self.img_current.areas,sum(self.img_current.areas))
        plt.bar(self.img_current.dias, y)
        plt.xlabel("Diameter").set_fontsize(6)
        plt.ylabel("Percent of Areas").set_fontsize(6)
        plt.title("Distribution histogram").set_fontsize(6)

        if Type == "Diameter":
            self.canvas1 = FigureCanvasTkAgg(f, self.viewhistdia)
            self.canvas1.draw() 
            self.canvas1.get_tk_widget().place(x=50, y=90, width=800, height=500)

        elif Type == "Area":
            self.canvas2 = FigureCanvasTkAgg(f, self.viewhistarea)
            self.canvas2.draw()
            self.canvas2.get_tk_widget().place(x=50, y=90, width=800, height=500)

if __name__ == "__main__":
    viewmain = ViewMain()






