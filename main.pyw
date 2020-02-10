import su.aes as aes
import wx
import wx.lib.newevent as WxNewevent
import os

finishedText, EVT_FIN_TEXT = WxNewevent.NewEvent()

class EncryptionFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="Encrypt", pos=(70, 70), size=(680, 420))

        self.textInp = wx.TextCtrl(self, -1, "When finished with text, close this window and then proceed with encrypting the text.", size=(680, 420), style=wx.TE_MULTILINE|wx.TE_PROCESS_ENTER)

        self.textInp.SetInsertionPoint(0)

        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnClose(self, event):
        global frame
        dlg = wx.MessageDialog(self, 'Confirmation?',
                            'Are you sure you are finished?', wx.ICON_QUESTION | wx.YES_NO | wx.YES_DEFAULT | wx.CANCEL)
        result = dlg.ShowModal()
        if result == wx.ID_CANCEL:
            self.Destroy()
            return
        if result == wx.ID_YES:
            dlg.Destroy()
            finalText = ""
            for i in range(self.textInp.GetNumberOfLines()):
                finalText = finalText + "\n" + self.textInp.GetLineText(i)
            finEvent = finishedText(content=finalText)
            wx.PostEvent(frame, finEvent)
            self.Destroy()
            return

        dlg.Destroy()

class DecryptionFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="Decrypt", pos=(70, 70), size=(680, 420))

        wildcard = "Encrypted File (*.enc)|*.enc|"     \
                "All files (*.*)|*.*"

        dlg = wx.FileDialog(
            self, message="Choose a file",
            defaultDir=os.getcwd(),
            defaultFile="",
            wildcard=wildcard,
            style=wx.FD_OPEN | wx.FD_MULTIPLE |
                  wx.FD_CHANGE_DIR | wx.FD_FILE_MUST_EXIST |
                  wx.FD_PREVIEW
            )

        choice = dlg.ShowModal()

        path = dlg.GetPath()
        dlg.Destroy()

        if choice == wx.ID_CANCEL:
            self.Destroy()
            return

        fObj = open(path, "r")
        f = fObj.read()

        while True:
            dlg1 = wx.TextEntryDialog(
                    self, 'Enter a key you wish to decrypt the text with.',
                    'Input', '', style=wx.OK | wx.CANCEL | wx.TE_PASSWORD )

            val = dlg1.ShowModal()

            if val == wx.ID_CANCEL:
                dlg1.Destroy()
                self.Destroy()
                return

            key = dlg1.GetValue()

            try:
                decryptedText = aes.decrypt(key, f)
                dlg1.Destroy()
                break
            except:
                dlg2 = wx.MessageDialog(self, 'Incorrect Password!', 'Error', wx.ICON_ERROR | wx.OK)

        self.textInp = wx.TextCtrl(self, -1, decryptedText, size=(680, 420), style=wx.TE_MULTILINE|wx.TE_PROCESS_ENTER|wx.TE_READONLY)

        self.textInp.SetInsertionPoint(0)



class MainBox(wx.Frame):
    def __init__(self, title):
        wx.Frame.__init__(self, None, title=title, pos=(50, 50), size=(980, 620))

        panel = wx.Panel(self, -1)
        self.SetBackgroundColour("WHITE")

        encryptButton = wx.Button(self, 10, "Encrypt", (330, 250), (80, 30))
        decryptButton = wx.Button(self, 20, "Decrypt", (490, 250), (80, 30))

        panel.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        encryptButton.Bind(wx.EVT_BUTTON, self.OnButtonEncrypt)
        decryptButton.Bind(wx.EVT_BUTTON, self.OnButtonDecrypt)
        self.Bind(EVT_FIN_TEXT, self.StartEncryption)
        panel.Layout()

    def OnKeyDown(self, event):
        if event.GetKeyCode() == 27:
            self.Destroy()

    def OnButtonEncrypt(self, event):
        global ROOT_DIR
        encryptFrame = EncryptionFrame()
        encryptFrame.SetIcon(wx.Icon(ROOT_DIR + "EncryptIcon.ico"))
        encryptFrame.Show(True)

    def StartEncryption(self, event):
        wildcard = "Encrypted File (*.enc)|*.enc|"     \
                "All files (*.*)|*.*"

        dlg = wx.TextEntryDialog(
                self, 'Enter a key you wish to encrypt the text with.',
                'Input', '', style=wx.OK | wx.CANCEL | wx.TE_PASSWORD)

        val = dlg.ShowModal()

        if val == wx.ID_CANCEL:
            dlg.Destroy()
            return

        key = dlg.GetValue()

        dlg.Destroy()

        encText = aes.encrypt(key, event.content)

        dlg1 = wx.FileDialog(
            self, message="Save file as ...", defaultDir=os.getcwd(),
            defaultFile="Untitled", wildcard=wildcard, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT
            )

        canceled = dlg1.ShowModal()

        path = dlg1.GetPath()

        if canceled == wx.ID_CANCEL:
            dlg1.Destroy()
            return

        fObj = open(path, "w")
        fObj.write(encText)

        dlg2 = wx.MessageDialog(self, 'File written at ' + path, 'Done', wx.ICON_INFORMATION | wx.OK)

        dlg2.ShowModal()
        dlg2.Destroy()

    def OnButtonDecrypt(self, event):
        global ROOT_DIR
        decryptFrame = DecryptionFrame()
        decryptFrame.SetIcon(wx.Icon(ROOT_DIR + "DecryptIcon.ico"))
        decryptFrame.Show(True)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) + "\\"

app = wx.App()
frame = MainBox("Safe Guard - A text editor")
frame.SetIcon(wx.Icon(ROOT_DIR + "MainIcon.ico"))
frame.Show(True)
app.MainLoop()