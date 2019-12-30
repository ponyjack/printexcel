from Tkinter import *
from PIL import Image, ImageTk, ImageGrab
import tkFileDialog, xlwings as xw
, tkMessageBox
, configparser
, types
, logging
, traceback
, time
, hashlib
, hmac

def raise_frame(frame):
    frame.tkraise()


root = Tk()
root.geometry('600x300')

def report_callback_exception(exc, val, tb):
    logging.exception('tkinker exception')


root.report_callback_exception = report_callback_exception

def create_window():
    window = Toplevel(root)
    return FullScreenApp(window)


class FullScreenApp(object):

    def __init__(self, master, **kwargs):
        self.master = master
        self.x, self.y = (0, 0)
        master.overrideredirect(1)
        self.selectim = None
        w, h = master.winfo_screenwidth(), master.winfo_screenheight()
        master.geometry(('{0}x{1}+0+0').format(w, h))
        self.tw = w
        self.th = h
        master.focus_set()
        master.bind('<Escape>', lambda e: self.OnQuit())
        self.photo = ImageTk.PhotoImage(ImageGrab.grab())
        self.canvas = Canvas(self.master, 6=w, 7=h)
        self.canvas.pack()
        self.canvas.create_image(w / 2, h / 2, 9=self.photo)
        self.rectt = self.canvas.create_rectangle(0, 0, w, h, 10='gray', 12='gray', 13='gray50')
        self.rectd = self.canvas.create_rectangle(0, 0, 0, 0, 10='gray', 12='gray', 13='gray50')
        self.rectlm = self.canvas.create_rectangle(0, 0, 0, 0, 10='gray', 12='gray', 13='gray50')
        self.rectrm = self.canvas.create_rectangle(0, 0, 0, 0, 10='gray', 12='gray', 13='gray50')
        self.canvas.bind('<ButtonPress-1>', self.on_button_press)
        self.canvas.bind('<B1-Motion>', self.on_move_press)
        self.canvas.bind('<ButtonRelease-1>', self.on_button_release)
        self.rect = None
        self.start_x = None
        self.start_y = None
        self.button = Button(self.master, 18='OK', 20=self.OnQuit)
        self.button.configure(6=20, 22=FLAT)
        self.buttonw = self.canvas.create_window(self.tw - self.tw / 10, self.th - self.th / 10, 24=self.button)
        return

    def on_button_press(self, event):
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        if not self.rect:
            self.rect = self.canvas.create_rectangle(self.x, self.y, 1, 1, 2='red')

    def on_move_press(self, event):
        curX = self.canvas.canvasx(event.x)
        curY = self.canvas.canvasy(event.y)
        self.curX = curX
        self.curY = curY
        self.canvas.coords(self.rect, self.start_x, self.start_y, curX, curY)
        self.canvas.coords(self.rectt, 0, 0, self.tw, self.start_y)
        self.canvas.coords(self.rectlm, 0, self.start_y, self.start_x, curY)
        self.canvas.coords(self.rectrm, curX, self.start_y, self.tw, curY)
        self.canvas.coords(self.rectd, 0, curY, self.tw, self.th)
        self.box = (
         self.start_x, self.start_y, self.curX, self.curY)

    def on_button_release(self, event):
        pass

    def OnQuit(self):
        im = ImageGrab.grab((self.start_x, self.start_y, self.curX, self.curY))
        self.selectim = im
        self.master.destroy()


class Panle:

    def __init__(self, root):
        self.datafile = ''
        self.templatefile = ''
        self.configfile = ''
        self.root = root
        rowindex = 0
        templatebutton = Button(root, 3='模板文件', 5=self.TemplateFie)
        templatebutton.grid(6=rowindex, 7=W + E + N + S, 8=5, 10=1)
        self.templatetext = Label(root)
        self.templatetext.grid(6=rowindex, 12=1, 13=2)
        self.image = Label(root, 15=20, 17=15)
        self.image.grid(6=rowindex, 12=3, 13=7, 21=7, 7=W + E + N + S, 8=5, 10=5)
        rowindex = rowindex + 1
        configbutton = Button(root, 3='配置文件', 5=self.ConfigFie)
        configbutton.grid(6=rowindex, 7=W + E + N + S, 8=5, 10=1)
        self.configtext = Label(root)
        self.configtext.grid(6=rowindex, 12=1, 13=2)
        rowindex = rowindex + 1
        databutton = Button(root, 3='数据文件', 5=self.DataFie)
        databutton.grid(6=rowindex, 7=W + E + N + S, 8=5, 10=1)
        self.datatext = Label(root)
        self.datatext.grid(6=rowindex, 12=1, 13=2)
        rowindex = rowindex + 1
        Label(root).grid(6=rowindex)
        rowindex = rowindex + 1
        Label(root).grid(6=rowindex)
        rowindex = rowindex + 1
        Label(root).grid(6=rowindex)
        rowindex = rowindex + 1
        Label(root).grid(6=rowindex)
        screenshotbutton = Button(root, 3='图片范围', 5=self.ScreenCapture)
        screenshotbutton.grid(6=rowindex, 12=0, 8=5, 7=W + E + N + S, 10=1)
        startbutton = Button(root, 3='生成图片', 5=self.Start)
        startbutton.grid(6=rowindex, 12=1, 8=5, 7=W + E + N + S, 10=1)
        k, v = root.grid_size()
        for i in range(0, v):
            root.columnconfigure(i, 26=1)

        for i in range(0, k):
            root.rowconfigure(i, 26=1)

    def TemplateFie(self):
        name = tkFileDialog.askopenfilename()
        try:
            self.templatxls = xw.Book(name)
            if name:
                self.templatefile = name
                self.templatetext['text'] = os.path.basename(name)
        except EXCEPTION as e:
            logging.exception('open xls fail')
            tkMessageBox.showinfo('Title', 'fail')

    def ConfigFie(self):
        name = tkFileDialog.askopenfilename()
        if name:
            try:
                c = configparser.ConfigParser()
                c.read(name)
                values = []
                values.extend(c['source'].values())
                values.extend(c['source'].keys())
                values.sort()
                print ('').join(values)
                crc = hmac.new(os.path.basename(name).encode('utf8'), ('').join(values), hashlib.sha1).hexdigest()
                if crc != c['crc']['key']:
                    tkMessageBox.showinfo('Title', '打开配置文件失败')
                    return
                self.conf = c
                self.configfile = name
                self.configtext['text'] = os.path.basename(name)
            except:
                logging.exception('open config fail')
                tkMessageBox.showinfo('Title', '打开配置文件失败')

    def DataFie(self):
        name = tkFileDialog.askopenfilename()
        if name:
            try:
                self.dataxls = xw.Book(name)
                if name:
                    self.datafile = name
                    self.datatext['text'] = os.path.basename(name)
            except EXCEPTION as e:
                logging.exception('open xls fail')
                tkMessageBox.showinfo('Title', 'fail')

    def ScreenCapture(self):
        self.root.iconify()
        self.templatxls.app.activate(True)
        self.templatxls.activate()
        self.root.deiconify()
        self.root.iconify()
        s = create_window()
        self.root.wait_window(s.master)
        self.root.update()
        if s.selectim:
            i = s.selectim.resize((self.image.winfo_width(),
             self.image.winfo_height()), Image.ANTIALIAS)
            im = ImageTk.PhotoImage(i)
            self.image.configure(1=im)
            self.image.image = im
            self.box = s.box
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
        cols = self.conf['source'].keys()
        if not os.path.exists('img'):
            os.makedirs('img')
        cindex = ''
        for i in range(2, 65536):
            values = []
            try:
                for c in cols:
                    cindex = c
                    value = s2[(c + str(i))].value
                    values.append(value)
                    if value:
                        s1[self.conf['source'][c]].value = value

                if sum(v == None for v in values) > len(values) / 2:
                    break
                time.sleep(0.2)
                img = ImageGrab.grab(self.box)
                name = 'img/' + str(s1[self.conf['file']['name']].value) + '.jpg'
                img.save(name)
            except Exception as e:
                logging.exception('get data fail %s%s' % (cindex, i))

        self.root.deiconify()
        tkMessageBox.showinfo('info', '完成')


Panle(root)
root.mainloop()
