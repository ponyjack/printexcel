# -*- coding: utf-8 -*-


from Tkinter import *
from PIL import Image, ImageTk, ImageGrab
import tkFileDialog
import os
import xlwings as xw
import tkMessageBox
import configparser
import types
import logging
import traceback
import time
import hashlib
import hmac

def raise_frame(frame):
    frame.tkraise()


root = Tk()
root.geometry("600x300")

def report_callback_exception(exc, val, tb):  
    # print(exc, val, tb)  # err = traceback.format_exception(*args)
    logging.exception("tkinker exception")
    # tkMessageBox.showerror('Exception', val)

root.report_callback_exception = report_callback_exception

def create_window():
    window = Toplevel(root)
    return FullScreenApp(window)


class FullScreenApp(object):
    def __init__(self, master, **kwargs):
        self.master = master
        self.x, self.y = 0, 0
        master.overrideredirect(1)
        self.selectim = None

        w, h = master.winfo_screenwidth(), master.winfo_screenheight()
        master.geometry(
            "{0}x{1}+0+0".format(w, h))
        # master.bind('<Escape>', self.toggle_geom)
        self.tw = w
        self.th = h
        master.focus_set()  # <-- move focus to this widget
        master.bind("<Escape>", lambda e: self.OnQuit())
        self.photo = ImageTk.PhotoImage(ImageGrab.grab())

        self.canvas = Canvas(self.master, width=w, height=h)

        # pack the canvas into a frame/form
        self.canvas.pack()

        # pic's upper left corner (NW) on the canvas is at x=50 y=10
        self.canvas.create_image(w/2, h/2, image=self.photo)
        self.rectt = self.canvas.create_rectangle(
            0, 0, w, h, fill="gray", outline="gray", stipple="gray50")
        self.rectd = self.canvas.create_rectangle(
            0, 0, 0, 0, fill="gray", outline="gray", stipple="gray50")
        self.rectlm = self.canvas.create_rectangle(
            0, 0, 0, 0, fill="gray", outline="gray", stipple="gray50")
        self.rectrm = self.canvas.create_rectangle(
            0, 0, 0, 0, fill="gray", outline="gray", stipple="gray50")
        # self.canvas.config(cursor='tcross')
        # self.canvas.create_rectangle(0, 0, w, h, fill=TRANSCOLOUR, outline=TRANSCOLOUR)

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

        self.rect = None

        self.start_x = None
        self.start_y = None

        self.button = Button(
            self.master, text="OK", command=self.OnQuit)
        self.button.configure(
            width=20, relief=FLAT)

        self.buttonw = self.canvas.create_window(
            self.tw - (self.tw / 10), self.th - (self.th/10), window=self.button)

    def on_button_press(self, event):
        # save mouse drag start position
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)

        # create rectangle if not yet exist
        if not self.rect:
            self.rect = self.canvas.create_rectangle(
                self.x, self.y, 1, 1, outline='red')

    def on_move_press(self, event):
        curX = self.canvas.canvasx(event.x)
        curY = self.canvas.canvasy(event.y)
        self.curX = curX
        self.curY = curY
        # expand rectangle as you drag the mouse
        self.canvas.coords(self.rect, self.start_x, self.start_y, curX, curY)

        self.canvas.coords(self.rectt, 0, 0, self.tw, self.start_y)
        self.canvas.coords(self.rectlm, 0, self.start_y, self.start_x, curY)
        self.canvas.coords(self.rectrm, curX,
                           self.start_y, self.tw, curY)
        self.canvas.coords(self.rectd, 0,
                           curY, self.tw, self.th)

        self.box = (self.start_x, self.start_y, self.curX, self.curY)

    def on_button_release(self, event):
        pass

    def OnQuit(self):
        im = ImageGrab.grab((self.start_x, self.start_y, self.curX, self.curY))
        # im.show()
        self.selectim = im
        self.master.destroy()


# root = tk.Tk()
# b = Button(root, text="Create new window", command=create_window)
# b.pack()

class Panle():
    def __init__(self, root):
        self.datafile = ""
        self.templatefile = ""
        self.configfile = ""
        self.root = root
        rowindex = 0

        templatebutton = Button(root, text=u"模板文件", command=self.TemplateFie)
        templatebutton.grid(
            row=rowindex, sticky=W+E+N+S, padx=5, pady=1)
        self.templatetext = Label(root)
        self.templatetext.grid(row=rowindex, column=1, columnspan=2)
        # ttext.config(state=DISABLED)

        # self.frame = Frame(root)
        self.image = Label(root, width=20, height=15)
        self.image.grid(row=rowindex, column=3, columnspan=7, rowspan=7,
                        sticky=W+E+N+S, padx=5, pady=5)
        # self.image.pack()
        rowindex = rowindex + 1
        # Label(root).grid(row=rowindex)

        # rowindex = rowindex + 1
        configbutton = Button(root, text=u"配置文件", command=self.ConfigFie)
        configbutton.grid(
            row=rowindex, sticky=W+E+N+S, padx=5, pady=1)

        self.configtext = Label(root)
        self.configtext.grid(row=rowindex,  column=1, columnspan=2)

        # ctext.config(state=DISABLED)
        rowindex = rowindex + 1
        # Label(root).grid(row=rowindex)
        # rowindex = rowindex + 1
        databutton = Button(root, text=u"数据文件", command=self.DataFie)
        databutton.grid(
            row=rowindex, sticky=W+E+N+S, padx=5, pady=1)

        self.datatext = Label(root)
        self.datatext.grid(row=rowindex, column=1, columnspan=2)

        rowindex = rowindex + 1
        Label(root).grid(row=rowindex)
        rowindex = rowindex + 1
        Label(root).grid(row=rowindex)
        rowindex = rowindex + 1
        Label(root).grid(row=rowindex)
        rowindex = rowindex + 1
        Label(root).grid(row=rowindex)

        screenshotbutton = Button(root, text=u"图片范围", command=self.ScreenCapture)
        screenshotbutton.grid(
            row=rowindex, column=0,  padx=5, sticky=W+E+N+S,  pady=1)

        startbutton = Button(root, text=u"生成图片", command=self.Start)
        startbutton.grid(
            row=rowindex, column=1,  padx=5, sticky=W+E+N+S,  pady=1)

        k, v = root.grid_size()

        # root.grid_columnconfigure(1, weight=100)

        for i in range(0, v):
            root.columnconfigure(i, weight=1)

        for i in range(0, k):
            root.rowconfigure(i, weight=1)

    def TemplateFie(self):
        name = tkFileDialog.askopenfilename()
        try:
            self.templatxls = xw.Book(name)
            if name:
                self.templatefile = name
                self.templatetext["text"] = os.path.basename(name)
        except EXCEPTION as e:
            logging.exception("open xls fail")
            tkMessageBox.showinfo("Title", "fail")


    def ConfigFie(self):
        name = tkFileDialog.askopenfilename()
        if name:
            try:
                c = configparser.ConfigParser()
                c.read(name)
                values = []
                values.extend(c["source"].values())
                values.extend(c["source"].keys())
                values.sort()
                print("".join(values))
                crc = hmac.new(os.path.basename(name).encode("utf8"), "".join(values), hashlib.sha1).hexdigest()
                if crc != c["crc"]["key"]:
                    tkMessageBox.showinfo("Title", "打开配置文件失败")
                    return

                self.conf = c
                self.configfile = name
                self.configtext["text"] = os.path.basename(name)
            except:
                logging.exception("open config fail")
                tkMessageBox.showinfo("Title", "打开配置文件失败")

    def DataFie(self):
        name = tkFileDialog.askopenfilename()
        if name:
            try:
                self.dataxls = xw.Book(name)
                if name:
                    self.datafile = name
                    self.datatext["text"] = os.path.basename(name)
            except EXCEPTION as e:
                logging.exception("open xls fail")
                tkMessageBox.showinfo("Title", "fail")

    def ScreenCapture(self):
        self.root.iconify()
        # print(xw.apps)
        # win32gui.SetForegroundWindow(self.templatxls.app.hwnd)

        self.templatxls.app.activate(True)

        self.templatxls.activate()
        self.root.deiconify()
        self.root.iconify()

        # win32gui.SetForegroundWindow(self.templatxls.app.hwnd)
        s = create_window()
        self.root.wait_window(s.master)
        self.root.update()

        if s.selectim:
            i = s.selectim.resize((self.image.winfo_width(),
                                   self.image.winfo_height()),  Image.ANTIALIAS)
            im = ImageTk.PhotoImage(i)
            self.image.configure(image=im)
            # print self.image.size()
            self.image.image = im
            self.box = s.box
            # self.image["text"] = str(im)
            self.root.update()
        self.root.deiconify()

    def Start(self):
        self.root.iconify()
        self.templatxls.app.activate(True)
        self.templatxls.activate()
        self.root.deiconify()
        self.root.iconify()

        s2 = self.dataxls.sheets[0]
        s1 = self.templatxls.sheets[0]

        cols = self.conf["source"].keys()

        if not os.path.exists("img"):
            os.makedirs("img")

        cindex = ""
        for i in range(2,  65536):
            values = []
            try:
                for c in cols:
                    cindex = c
                    value = s2[c+str(i)].value
                    values.append(value)

                    if value:
                        s1[self.conf["source"][c]].value = value
                if sum(v == None for v in values) > (len(values)/2):
                    break
                time.sleep(0.2)
                img = ImageGrab.grab(self.box)
                name = "img/"+str(s1[self.conf["file"]['name']].value) + ".jpg"
                img.save(name)
            except Exception as e:
                logging.exception("get data fail %s%s"%(cindex,i))
                
                
        self.root.deiconify()
        tkMessageBox.showinfo("info", "完成")

Panle(root)
# Label(root).pack()
root.mainloop()
                                    
