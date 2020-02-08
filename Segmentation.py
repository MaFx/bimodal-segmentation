import Image
import os
import wx

background = 0

class Example(wx.Frame):
    
    def __init__(self, *args, **kwargs):
        super(Example, self).__init__(*args, **kwargs)
        self.args = args
        self.kwargs = kwargs
        self.fname=""    
        self.InitUI()        
        #self.SetIcon(wx.Icon('favicon.ico',wx.BITMAP_TYPE_ICO))
        
    def InitUI(self):    

        menubar = wx.MenuBar() 
        self.fileMenu = wx.Menu()
        fopen = self.fileMenu.Append(wx.ID_OPEN, 'Open Image', 'Load Image')
        self.Bind(wx.EVT_MENU, self.OnOpen,fopen)
        fitem = self.fileMenu.Append(wx.ID_EXIT, 'Quit', 'Quit application')
        self.Bind(wx.EVT_MENU, self.OnQuit, fitem)
        menubar.Append(self.fileMenu, '&File')

        self.fMenu2 = wx.Menu()
        self.Light = self.fMenu2.Append(9,'Light', 'Dark object on light background', kind=wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU, self.OnLight,self.Light)
        self.Dark = self.fMenu2.Append(10,'Dark', 'Light object on dark background', kind=wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU, self.OnDark,self.Dark)
        self.fMenu2.Check(self.Dark.GetId(), True)
        menubar.Append(self.fMenu2, '&Background color')
        
        self.fMenu3 = wx.Menu()
        self.SEGMo = self.fMenu3.Append(13,'Segmentation', 'Bimodal Segmentation')
        self.Bind(wx.EVT_MENU, self.Segment,self.SEGMo)
        menubar.Append(self.fMenu3, '&Operation')

        menuAbout = wx.Menu()
        menuAbout.Append(2, "&About...", "About this program")
        self.Bind(wx.EVT_MENU, self.OnAbout, id=2)
        menubar.Append(menuAbout, '&Help')

        self.SetMenuBar(menubar)
        self.opened = False
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.statusBar = self.CreateStatusBar()
        self.Bind(wx.EVT_SIZE, self.OnSize)

        self.SetSize((800, 520))
        self.SetTitle('Image Segmentation')
        self.Centre()
        self.Show(True)

    def OnLight(self, event):
        global background
        background = 1
        self.fMenu2.Check(self.Light.GetId(), True)
        self.fMenu2.Check(self.Dark.GetId(), False)
        
    def OnDark(self, event):
        global background
        background = 0
        self.fMenu2.Check(self.Light.GetId(), False)
        self.fMenu2.Check(self.Dark.GetId(), True)
        
    def OnSize(self,event):
        if self.opened == True:
            self.dc.DrawBitmap(self.bitmap, 10,10)
        

    def Segment(self,event):
        tmp = 0
        th = otsu_thrd(self.image)
        out_img = segment(self.image, th)
        self.bitmap = PilImageToWxBitmap(out_img)
        self.dc.DrawBitmap(self.bitmap, 10,10)        

    def OnOpen(self, event):
        global Timage
        filters = 'Image files (*.png;*.jpg;*.gif)|*.png;*.jpg;*.gif'
        dialog = wx.FileDialog(self, message="Open an Image...", defaultDir=os.getcwd(), defaultFile="", wildcard=filters, style=wx.OPEN)
        if dialog.ShowModal() == wx.ID_OK:
            self.opened = True
            self.fname = dialog.GetPath()
            self.image = Image.open(self.fname)
            width, height = self.image.size
            if width > 760 :
                aspect = width * 1.0 / height
                maxheight = 760 / aspect
                height = maxheight
                self.image = self.image.resize((760,int(maxheight)))
            if height > 550 :
                self.SetSize((width+40,height+100))
            Timage = self.image
            self.bitmap = PilImageToWxBitmap(self.image)
            self.dc.DrawBitmap(self.bitmap, 10,10)
            self.statusBar.SetStatusText('Image Loaded') 
        dialog.Destroy()


    def OnPaint(self, event):
        self.dc = wx.PaintDC(self)
        
    def OnQuit(self, e):
        self.Close()
        
    def OnAbout(self, event):
        AboutFrame().Show()

############################################################################################
class AboutFrame(wx.Frame):

    title = "About"

    def __init__(self):
        wx.Frame.__init__(self, wx.GetApp().TopWindow, title=self.title)
        panel = wx.Panel(self,-1)
        text = "Created by\nMartins Fridenbergs\n2012\nDeveloped in Python"
        font = wx.Font(10,wx.ROMAN,wx.NORMAL,wx.NORMAL)
        statictext = wx.StaticText(panel,-1,text,(30,20),style = wx.ALIGN_CENTRE)
        statictext.SetFont(font)
        self.Center()
        self.SetSize((200,150))      

############################################################################################# 
def PilImageToWxBitmap( myPilImage ) :
    return WxImageToWxBitmap( PilImageToWxImage( myPilImage ) ) 

def PilImageToWxImage( myPilImage ):
    myWxImage = wx.EmptyImage( myPilImage.size[0], myPilImage.size[1] )
    myWxImage.SetData( myPilImage.convert( 'RGB' ).tostring() )
    return myWxImage

def WxImageToWxBitmap( myWxImage ) :
    return myWxImage.ConvertToBitmap()

#############################################################################################
def otsu_thrd(im):
    width, height = im.size    
    hist_data = im.histogram()
    
    sum_all_rgb = 0
    for t in range(256):
        sum_all_rgb += t * (hist_data[t] + t * hist_data[t+256] +t * hist_data[t+512])/3


    sum_back, w_back, w_fore, var_max, threshold = 0, 0, 0, 0, 0
    total = height*width
    for t in range(256):
        w_back += (hist_data[t] + hist_data[t+256] + hist_data[t+512])/3 # Weight Background
        if (w_back == 0):
            continue
       
        w_fore = total - w_back # Weight Foreground
        if (w_fore == 0) :
            break

        sum_back += t * (hist_data[t] + hist_data[t+256] + hist_data[t+512])/3


        mean_back = sum_back / w_back # Mean Background
        mean_fore = (sum_all_rgb - sum_back) / w_fore # Mean Foreground

        # Calculate Between Class Variance
        var_between = w_back * w_fore * (mean_back - mean_fore)**2       

        # Check if new maximum found
        if (var_between > var_max):
            var_max = var_between
            threshold = t/3
    return threshold  




def segment(im, thrd = 128):
    global background
    mat = im.load()
    width, height = im.size
    out = Image.new('RGB',(width, height))
    out_pix = out.load()    

    for y in range(height):
        for x in range(width):
            tmp = ( mat[x,y][0]+mat[x,y][1]+mat[x,y][2])/3
            if tmp >= thrd:
                if background == 0:
                    out_pix[x,y] = ( mat[x,y][0],mat[x,y][1],mat[x,y][2])
                else :
                    out_pix[x, y] = (255,255,255)
            else:
                if background == 0:
                    out_pix[x, y] = (0,0,0)
                else :
                    out_pix[x,y] = ( mat[x,y][0],mat[x,y][1],mat[x,y][2] )

    return out

#############################################################################################
if __name__ == '__main__':
    ex = wx.App()
    main = Example(None)
    ex.MainLoop()
