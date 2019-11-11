# config utf-8
"""
wxpythonのGUIを使用したFANUC型NCデータのコンバータ。
このファイルはGUI処理が決めているだけです。

データの解析方法を変更したい場合は'.\lib\langs内のファイルを編集すること。
新たに変換方法を追加するには
'.\lib\conversion_methods_for_fanuc\_method.py' の
'ConversionMethod' を継承し、'convert' メソッドで変換の仕方を定義したclassを
'conversion_methods_for_fanuc' パッケージにimportさせることで追加出来る。

<使い方>
NCファイルを FileMenu -> Openから指定する もしくは メインウィンドウにDnDすることで
そのデータの字句解析を行い、プログラム毎に変換可能な状態となる。
字句解析を行った際に不正な字句が見つかった場合、
コンソール画面に 'ParseError' として、このプログラム名の, このブロックが, このように認識されました
と出力されるため確認すること。

プログラム一覧からプログラム名を右クリックすることで、
メインウィンドウ右側に位置するテキストボックスに、そのプログラムの内容を表示させることが出来る。
あくまで確認用であるため、プログラムの編集はテキストボックス上では一切出来ない。

変換するプログラムを選んだら、変換方法を選び変換を行い Fileから保存して終了。
エラーが起これば 'NcError' が表示されるためコンソールを確認すること。
"""
import traceback
import os
import lib.nc
from lib.conversion_methods_for_fanuc._method import ConversionMethod
import lib.conversion_methods_for_fanuc
try:
    import wx
    import wx.adv
    import regex
except:
    traceback.print_exc()

def show_about():
    info = wx.adv.AboutDialogInfo()
    info.SetName('FanucDataConverer')
    info.SetDescription(__doc__)
    info.AddDeveloper('Sun')
    wx.adv.AboutBox(info)

def get_conv_method_attr(str):
    return getattr(lib.conversion_methods_for_fanuc, str)

def get_nclang():
    return lib.nc.langs.fanuc.Fanuc()

# 'conversion_methods_for_fanuc' パッケージ内の 'ConversionMethod' を継承したクラスのみを抽出したリスト
CONV_METHODS = []
for i in dir(lib.conversion_methods_for_fanuc):
    try:
        instance = get_conv_method_attr(i)()
        if isinstance(instance, ConversionMethod):
            CONV_METHODS.append(i)
    except:
        pass

INTRODUCTION_TEXT = [
"""
--> Step1. Open a Nc file.
    Step2. Choose the programs you want to convert from the listbox on the left.
    Step3. Choose the conversion method.
""",
"""
    Step1. Open a Nc file.
--> Step2. Choose the programs you want to convert from the listbox on the left.
    Step3. Choose the conversion method.
""",
"""
    Step1. Open a Nc file.
    Step2. Choose the programs you want to convert from the listbox on the left.
--> Step3. Choose the conversion method.
"""
]

def open_filedialog(cmd):
    """wxpython のファイルダイアログを開き、返り値にパス名を得る。
    引数で 'open' を指定した場合は 開く、
    'saveas' を指定した場合は 名前をつけて保存 のダイアログを開く。
    """
    if cmd.lower() == 'open':
        title = "Open Ncfile"
        style = wx.FD_OPEN
    elif cmd.lower() == 'saveas':
        title = "SaveAs Ncfile"
        style = wx.FD_SAVE
    else:
        return
    with wx.FileDialog(None, title, style=style) as fileDialog:
        if fileDialog.ShowModal() == wx.ID_CANCEL:
            return
        return fileDialog.GetPath()

class DnDTarget(wx.FileDropTarget):
    """DnDを検出した場合、そのファイルを開く"""
    def __init__(self, parent):
        super().__init__()
        self._parent = parent

    @property
    def parent(self):
        return self._parent

    def OnDropFiles(self, x, y, files):
        self.parent.open_nc_file(files[0])
        return True

class TextViewPanel(wx.Panel):
    """NCプログラム確認用のパネル"""
    def __init__(self, parent):
        super().__init__(parent)
        self._create_widgets()
        self._set_layout()

    @property
    def introduct(self):
        return self._introduct
    @property
    def program(self):
        return self._program

    def _create_widgets(self):
        self._introduct = wx.StaticText(self, -1, INTRODUCTION_TEXT[0])
        self._program = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_DONTWRAP)

    def _set_layout(self):
        sizer = wx.GridBagSizer(10)
        sizer.Add(self.introduct, (1, 2), (1, 1), flag=wx.ALIGN_CENTER)
        sizer.Add(self.program, (2, 1), (1, 3), flag=wx.EXPAND)
        self.SetSizer(sizer)
        sizer.AddGrowableRow(2)
        sizer.AddGrowableCol(1, 0.5)
        sizer.AddGrowableCol(2, 1)
        sizer.AddGrowableCol(3, 0.5)
        self.SetBackgroundColour(COLOR_MAIN_LABEL[0])
        self.introduct.SetBackgroundColour(COLOR_INTRODUCT[0])
        self.introduct.SetForegroundColour(COLOR_INTRODUCT[1])
        self.introduct.SetFont(FONT)
        self.program.SetBackgroundColour(COLOR_TEXTCTRL[0])
        self.program.SetForegroundColour(COLOR_TEXTCTRL[1])
        self.program.SetFont(FONT)

class MainWindow(wx.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._create_menu()
        self._create_widgets()
        self._set_events()
        self._set_layout()
        self.Center()
        self.Show()
        self._sub_window = SubWindow(self, size=(900, 600))

    @property
    def sub_window(self):
        return self._sub_window
    @property
    def list_program(self):
        return self._list_program
    @property
    def viewer(self):
        return self._viewer
    @property
    def button_choose(self):
        return self._button_choose
    @property
    def ncdata(self):
        return self._ncdata

    def _create_menu(self):
        menu_main = wx.MenuBar()
        file_menu = wx.Menu()
        help_menu = wx.Menu()
        file_menu.Append(wx.ID_OPEN, '&Open')
        file_menu.Append(wx.ID_SAVEAS,'&SaveAs')
        help_menu.Append(wx.ID_ABOUT,'&About')
        menu_main.Append(file_menu, "&File")
        menu_main.Append(help_menu, "&Help")
        self.SetMenuBar(menu_main)

    def _create_widgets(self):
        self._list_program = wx.ListBox(self, -1, style=wx.LB_NEEDED_SB|wx.LB_EXTENDED|wx.LB_OWNERDRAW)
        self._viewer = TextViewPanel(self)
        self._button_choose = wx.Button(self, -1, 'Choose the conversion method.')

    def _set_events(self):
        self.SetDropTarget(DnDTarget(self))
        self.Bind(wx.EVT_MENU, self.OnClickMenu)
        self.button_choose.Bind(wx.EVT_BUTTON, self.OnPress)
        self.list_program.Bind(wx.EVT_LISTBOX, self.OnSelect)
        self.list_program.Bind(wx.EVT_RIGHT_DOWN, self.OnSelectRight)

    def _set_layout(self):
        sizer = wx.GridBagSizer()
        sizer.Add(self.list_program, (0, 0), (1, 1), flag=wx.EXPAND)
        sizer.Add(self.viewer, (0, 1), (1, 1), flag=wx.EXPAND)
        sizer.Add(self.button_choose, (1, 0), (1, 2), flag=wx.EXPAND)
        sizer.AddGrowableCol(0, 1)
        sizer.AddGrowableCol(1, 10)
        sizer.AddGrowableRow(0, 10)
        sizer.AddGrowableRow(1, 1)
        self.SetSizer(sizer)
        self.list_program.SetBackgroundColour(COLOR_PROGRAM_LIST[0][0])
        self.list_program.SetFont(FONT)
        self.button_choose.SetFont(FONT)

    def OnClickMenu(self, event):
        id = event.GetId()
        if id == wx.ID_OPEN:
            self.OnOpen()
        elif id == wx.ID_SAVEAS:
            self.OnSaveAs()
        elif id == wx.ID_ABOUT:
            show_about()

    def OnOpen(self):
        path = open_filedialog('open')
        if not path:
            return
        self.open_nc_file(path)

    def OnSaveAs(self):
        if not self.list_program.GetCount():
            return
        path = open_filedialog('saveas')
        if not path:
            return
        try:
            with open(path, 'w') as f:
                for k, v in self.ncdata.items():
                    f.write(str(v))
        except:
            wx.MessageDialog(self, 'It could not be successfully processed.').ShowModal()
            traceback.print_exc()
        else:
            wx.MessageDialog(self, 'Successfully processed.').ShowModal()

    def OnPress(self, event):
        if not self.list_program.GetSelections():
            return
        if self.sub_window.IsShown():
            self.sub_window.SetFocus()
        else:
            self.sub_window.Show()

    def OnSelect(self, event):
        self.viewer.introduct.SetLabel(INTRODUCTION_TEXT[2])

    def OnSelectRight(self, event):
        """プログラム名を右クリックすることで、右テキストパネルでNCプログラムの確認ができる。"""
        i = self.list_program.HitTest(event.GetPosition())
        if i == -1:
            return
        self.list_program.Refresh()
        self.init_color_program_list()
        self.list_program.SetItemBackgroundColour(i, COLOR_PROGRAM_LIST[1][0])
        self.list_program.SetItemForegroundColour(i, COLOR_PROGRAM_LIST[1][1])
        key = self.list_program.GetString(i)
        self.viewer.program.ChangeValue(str(self.ncdata[key]))
        self.viewer.program.ShowPosition(0)

    def open_nc_file(self, path):
        os.system('cls') # コンソール初期化
        with open(path, 'r') as f:
            nclang = get_nclang()
            nclang.store_data(f)
            self._ncdata = nclang.data
            self.list_program.SetItems(self.ncdata.keys())
            self.init_color_program_list()
            self.viewer.introduct.SetLabel(INTRODUCTION_TEXT[1])
            self.viewer.program.Clear()

    def init_color_program_list(self):
        """ 'list_program' は flag で wx.LB_OWNERDRAWを使用しているため
        アイテム毎にそれぞれ個別の背景色・文字色を持っていて、一度色を変えると元に戻すのが面倒。
        全てのアイテムを初期色に戻したい場合に、このメソッドを使用する。"""
        for i in range(self.list_program.GetCount()):
            self.list_program.SetItemBackgroundColour(i, COLOR_PROGRAM_LIST[0][0])
            self.list_program.SetItemForegroundColour(i, COLOR_PROGRAM_LIST[0][1])

class SubWindow(wx.Frame):
    """変換方法を選択するサブウィンドウ"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._parent = parent
        self._create_widgets()
        self._set_events()
        self._set_layout()
        self._init_widgets()
        self.Center()

    @property
    def parent(self):
        return self._parent
    @property
    def list_method(self):
        return self._list_method
    @property
    def docstring(self):
        return self._docstring
    @property
    def button_convert(self):
        return self._button_convert

    def _create_widgets(self):
        self._list_method = wx.ListBox(self, -1, style=wx.LB_NEEDED_SB)
        self._docstring = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE|wx.TE_READONLY)
        self._button_convert = wx.Button(self, -1, 'Start conversion')

    def _set_events(self):
        self.Bind(wx.EVT_CLOSE, self.OnExit)
        self.list_method.Bind(wx.EVT_LISTBOX, self.OnSelect)
        self.button_convert.Bind(wx.EVT_BUTTON, self.OnPress)

    def _set_layout(self):
        sizer = wx.GridBagSizer()
        sizer.Add(self.list_method, (0, 0), (1, 1), flag=wx.EXPAND)
        sizer.Add(self.docstring, (0, 1), (1, 1), flag=wx.EXPAND)
        sizer.Add(self.button_convert, (1, 0), (1, 2), flag=wx.EXPAND)
        sizer.AddGrowableRow(0, 8)
        sizer.AddGrowableRow(1, 1)
        sizer.AddGrowableCol(1, 0)
        self.SetSizer(sizer)
        self.list_method.SetBackgroundColour(COLOR_LISTBOX[0])
        self.list_method.SetForegroundColour(COLOR_LISTBOX[1])
        self.list_method.SetFont(FONT)
        self.docstring.SetBackgroundColour(COLOR_TEXTCTRL[0])
        self.docstring.SetForegroundColour(COLOR_TEXTCTRL[1])
        self.docstring.SetFont(FONT)
        self.button_convert.SetFont(FONT)

    def _init_widgets(self):
        self.list_method.SetItems(CONV_METHODS)

    def OnSelect(self, event):
        i = self.list_method.GetSelection()
        s = self.list_method.GetString(i)
        doc = get_conv_method_attr(s).__doc__
        self.docstring.ChangeValue(doc)
        self.docstring.ShowPosition(0)

    def OnPress(self, event):
        i = self.list_method.GetSelection()
        if i == -1:
            return
        method_name = self.list_method.GetString(i)
        method_inst = get_conv_method_attr(method_name)()
        keys = [self.parent.list_program.GetString(i) for i in self.parent.list_program.GetSelections()]
        #'list_program' で選ばれたアイテムが6つ以上である場合、5つ毎に改行を入れて見やすい形に変える。
        trgs = '\n  '.join([', '.join(keys[idx:idx + 5]) for idx in range(0, len(keys), 5)])
        msg = """Start conversion.
method:
  {0}
target:
  {1}
""".format(method_name, trgs)
        if wx.MessageDialog(self, msg, 'Confirm', wx.OK | wx.CANCEL).ShowModal() == wx.ID_OK:
            try:
                for k in keys:
                    method_inst.convert(self.parent.ncdata[k])
            except:
                wx.MessageDialog('It could not be successfully processed.').ShowModal()
                traceback.print_exc()
            else:
                wx.MessageDialog(self, 'Successfully processed conversion').ShowModal()

    def OnExit(self, event):
        self.Hide()

def main():
    global FONT, COLOR_MAIN_LABEL, COLOR_INTRODUCT, COLOR_TEXTCTRL, COLOR_LISTBOX, COLOR_PROGRAM_LIST

    app = wx.App(False)
    FONT = wx.Font(
        12,
        wx.FONTFAMILY_DEFAULT,
        wx.FONTSTYLE_NORMAL,
        wx.FONTWEIGHT_NORMAL,
        faceName='Ricty Diminished'
    )
    #COLOR (bg-color, fg-color)
    COLOR_MAIN_LABEL = ('#2b2c30', '#2b2c30')
    COLOR_INTRODUCT = ('#2e333a', '#59697f')
    COLOR_TEXTCTRL = ('#bcc0c6', '#2b2c30')
    COLOR_LISTBOX = ('#343d47', '#9098a5')
    COLOR_PROGRAM_LIST = (
        COLOR_LISTBOX, # デフォルト色
        ('#5e6063', '#ddb5b5') # 右クリックされたアイテムのハイライト色
    )
    MainWindow(None, size=(1000, 700))
    app.MainLoop()

if __name__ == '__main__':
    main()
