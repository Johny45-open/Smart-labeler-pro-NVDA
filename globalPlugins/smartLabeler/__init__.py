import globalPluginHandler
import api
import ui
import wx
import json
import os
from .dialogs import LabelManagerDialog

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    def __init__(self):
        super(GlobalPlugin, self).__init__()
        self.data_path = os.path.join(os.path.dirname(__file__), 'labels.json')
        self.labels = self.load_labels()
        self.pending_key = None
        self.last_focused_key = None
        self.last_label_index = 0

    def load_labels(self):
        if os.path.exists(self.data_path):
            try:
                with open(self.data_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_labels(self, labels_to_save=None):
        try:
            data = labels_to_save if labels_to_save is not None else self.labels
            with open(self.data_path, 'w', encoding='utf-8') as f:
                if not data:
                    f.write('{}')
                else:
                    json.dump(data, f, ensure_ascii=False, indent=4)
        except:
            pass

    def _get_key(self, obj):
        import re
        
        def sanitize(text):
            return re.sub(r'\d+', '', str(text)).strip()

        app_name = obj.appModule.appName if obj.appModule else 'unknown'
        role = sanitize(getattr(obj, 'role', ''))
        name = sanitize(getattr(obj, 'name', ''))
        
        uia_class = sanitize(getattr(obj, 'UIAClassName', ''))
        if not uia_class:
            uia_class = sanitize(getattr(obj, 'windowClassName', ''))
        
        path = []
        p = obj.parent
        while p:
            role_p = sanitize(str(p.role))
            if role_p:
                path.append(role_p)
            p = p.parent
        path_str = "->".join(path)
        
        key = f'{app_name}:{uia_class}:{role}:{name}:{path_str}'
        return re.sub(r'\d+', '', key)

    def event_gainFocus(self, obj, nextHandler):
        nextHandler()
        
        if not os.path.exists(self.data_path):
            self.labels = {}
        else:
            self.labels = self.load_labels()
        
        key = self._get_key(obj)
        self.last_focused_key = key
        self.last_label_index = 0
        
        if key in self.labels:
            labels_list = self.labels[key]
            if isinstance(labels_list, list) and len(labels_list) > 0:
                ui.message(labels_list[0])
            elif isinstance(labels_list, str) and labels_list:
                ui.message(labels_list)

    def script_speakAdditionalInfo(self, gesture):
        """Přečte další popisek v pořadí pro aktuální prvek."""
        obj = api.getFocusObject()
        if not obj: return
        key = self._get_key(obj)
        
        if key not in self.labels:
            ui.message("Žádné další informace nejsou k dispozici.")
            return
            
        labels_list = self.labels[key]
        if not isinstance(labels_list, list) or len(labels_list) <= 1:
            ui.message("Žádné další informace pro tento prvek.")
            return
            
        if key != self.last_focused_key:
            self.last_focused_key = key
            self.last_label_index = 0
            
        self.last_label_index = (self.last_label_index + 1) % len(labels_list)
        ui.message(labels_list[self.last_label_index])

    def script_prepareLabel(self, gesture):
        """Příprava objektu pro pojmenování. Po stisku je nutné zkopírovat text do schránky a potvrdit zkratkou NVDA+Ctrl+Shift+L."""
        obj = api.getFocusObject()
        if not obj:
            ui.message('Nebylo možné získat fokus.')
            return
        self.pending_key = self._get_key(obj)
        ui.message('Objekt připraven k pojmenování. Zkopírujte text do schránky a stiskněte NVDA+Ctrl+Shift+L pro uložení.')

    def script_saveFromClipboard(self, gesture):
        """Uloží obsah schránky jako popisky pro naposledy vybraný objekt."""
        if not self.pending_key:
            ui.message('Nejprve vyberte objekt pomocí NVDA+Ctrl+L.')
            return
        dataObj = wx.TextDataObject()
        if wx.TheClipboard.Open():
            success = wx.TheClipboard.GetData(dataObj)
            wx.TheClipboard.Close()
            if success:
                text = dataObj.GetText().strip()
                if text:
                    lines = [line.strip() for line in text.splitlines() if line.strip()]
                    self.labels[self.pending_key] = lines
                    self.save_labels(self.labels)
                    ui.message(f"Uloženo {len(lines)} popisků: {lines[0]}")
                else:
                    ui.message('Schránka je prázdná.')
        self.pending_key = None

    def script_appendFromClipboard(self, gesture):
        """Přidá text ze schránky jako další popisek k aktuálnímu objektu."""
        obj = api.getFocusObject()
        if not obj:
            ui.message('Nebylo možné získat fokus.')
            return
        key = self._get_key(obj)
        
        dataObj = wx.TextDataObject()
        if wx.TheClipboard.Open():
            success = wx.TheClipboard.GetData(dataObj)
            wx.TheClipboard.Close()
            if success:
                text = dataObj.GetText().strip()
                if text:
                    if key not in self.labels:
                        self.labels[key] = []
                    if isinstance(self.labels[key], str):
                        self.labels[key] = [self.labels[key]]
                    new_lines = [line.strip() for line in text.splitlines() if line.strip()]
                    self.labels[key].extend(new_lines)
                    self.save_labels(self.labels)
                    ui.message(f"Přidáno: {len(new_lines)} popisků. Celkem: {len(self.labels[key])}. Aktuální: {self.labels[key][-1]}")
    
    def script_manageLabels(self, gesture):
        """Otevře dialog pro správu uložených popisků."""
        self.labels = self.load_labels()
        
        def show_dialog():
            dlg = LabelManagerDialog(None, self)
            if dlg.ShowModal() == wx.ID_OK:
                self.labels = self.load_labels()
            dlg.Destroy()
            
        wx.CallAfter(show_dialog)

    __gestures = {
        'kb:NVDA+control+l': 'prepareLabel',
        'kb:NVDA+control+shift+l': 'saveFromClipboard',
        'kb:NVDA+control+alt+a': 'appendFromClipboard',
        'kb:NVDA+control+alt+l': 'manageLabels',
        'kb:NVDA+alt+l': 'speakAdditionalInfo'
    }