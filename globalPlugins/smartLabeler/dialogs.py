import wx

class LabelManagerDialog(wx.Dialog):
    def __init__(self, parent, labels):
        super().__init__(parent, title="Správa popisků SmartLabeler", size=(600, 600))
        self.labels = labels
        self.selected_key = None
        self.init_ui()

    def init_ui(self):
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Seznam prvků
        self.list_ctrl = wx.ListBox(panel, choices=list(self.labels.keys()))
        sizer.Add(wx.StaticText(panel, label="Vyberte prvek:"), 0, wx.ALL, 5)
        sizer.Add(self.list_ctrl, 1, wx.EXPAND | wx.ALL, 5)

        # Tlačítko pro smazání prvku
        del_item_btn = wx.Button(panel, label="Smazat celý prvek")
        sizer.Add(del_item_btn, 0, wx.ALL, 5)

        # Pole pro úpravu popisků
        self.text_ctrl = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
        sizer.Add(wx.StaticText(panel, label="Popisky (každý na novém řádku):"), 0, wx.ALL, 5)
        sizer.Add(self.text_ctrl, 1, wx.EXPAND | wx.ALL, 5)

        # Tlačítka
        btn_sizer = wx.StdDialogButtonSizer()
        save_btn = wx.Button(panel, wx.ID_OK, label="Uložit")
        cancel_btn = wx.Button(panel, wx.ID_CANCEL, label="Zrušit")
        btn_sizer.AddButton(save_btn)
        btn_sizer.AddButton(cancel_btn)
        btn_sizer.Realize()
        sizer.Add(btn_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        panel.SetSizer(sizer)
        
        # Události
        self.list_ctrl.Bind(wx.EVT_LISTBOX, self.on_select)
        save_btn.Bind(wx.EVT_BUTTON, self.on_save)
        del_item_btn.Bind(wx.EVT_BUTTON, self.on_delete_item)
        
        self.list_ctrl.SetFocus()

    def on_select(self, event):
        self.selected_key = self.list_ctrl.GetStringSelection()
        labels = self.labels.get(self.selected_key, [])
        if isinstance(labels, list):
            self.text_ctrl.SetValue("\n".join(labels))
        else:
            self.text_ctrl.SetValue(str(labels))

    def on_delete_item(self, event):
        if not self.selected_key:
            return
        
        if wx.MessageBox(f"Opravdu chcete smazat všechny popisky pro prvek '{self.selected_key}'?", 
                         "Potvrzení smazání", wx.YES_NO | wx.ICON_QUESTION) == wx.YES:
            del self.labels[self.selected_key]
            self.list_ctrl.Delete(self.list_ctrl.GetSelection())
            self.text_ctrl.Clear()
            self.selected_key = None
            wx.MessageBox("Prvek smazán.", "Info", wx.OK | wx.ICON_INFORMATION)

    def on_save(self, event):
        if not self.selected_key:
            # Pokud nic není vybráno, jen zavřeme dialog
            self.EndModal(wx.ID_CANCEL)
            return
        
        new_text = self.text_ctrl.GetValue()
        new_labels = [line.strip() for line in new_text.splitlines() if line.strip()]
        self.labels[self.selected_key] = new_labels
        self.EndModal(wx.ID_OK)
