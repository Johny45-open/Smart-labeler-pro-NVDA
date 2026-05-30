import globalPluginHandler
import api
import ui
import wx
import json
import os
import subprocess

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

    def save_labels(self):
        with open(self.data_path, 'w', encoding='utf-8') as f:
            json.dump(self.labels, f, ensure_ascii=False, indent=4)

    def _get_obj_index(self, obj):
        try:
            return obj.indexInParent
        except:
            return 0

    def _get_key(self, obj):
        app_name = obj.appModule.appName if obj.appModule else 'unknown'
        automation_id = getattr(obj, 'automationID', '')
        role = getattr(obj, 'role', '')
        name = getattr(obj, 'name', '')
        window_class = obj.windowClassName
        path = []
        p = obj.parent
        while p:
            if p.name:
                path.append(p.name)
            p = p.parent
        path_str = "->".join(path)
        index = self._get_obj_index(obj)
        return f'{app_name}:{window_class}:{automation_id}:{role}:{name}:{path_str}:{index}'

    def event_gainFocus(self, obj, nextHandler):
        nextHandler()
        self.labels = self.load_labels()
        key = self._get_key(obj)
        self.last_focused_key = key
        self.last_label_index = 0
        
        if key in self.labels:
            labels_list = self.labels[key]
            if isinstance(labels_list, list) and len(labels_list) > 0:
                ui.message(labels_list[0])
            elif isinstance(labels_list, str):
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
        obj = api.getFocusObject()
        if not obj:
            ui.message('Nebylo možné získat fokus.')
            return
        self.pending_key = self._get_key(obj)
        ui.message('Objekt připraven k pojmenování. Zkopírujte jeden nebo více řádků do schránky a stiskněte NVDA+Ctrl+Shift+L pro uložení.')

    def script_saveFromClipboard(self, gesture):
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
                    self.save_labels()
                    ui.message(f'Uloženo {len(lines)} popisků.')
                else:
                    ui.message('Schránka je prázdná.')
            else:
                ui.message('Nepodařilo se přečíst schránku.')
        else:
            ui.message('Nepodařilo se otevřít schránku.')
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
                    self.save_labels()
                    ui.message(f'Přidáno {len(new_lines)} popisků. Celkem: {len(self.labels[key])}')
                else:
                    ui.message('Schránka je prázdná.')
            else:
                ui.message('Nepodařilo se přečíst schránku.')
        else:
            ui.message('Nepodařilo se otevřít schránku.')
    
    def script_manageLabels(self, gesture):
        if os.path.exists(self.data_path):
            os.startfile(self.data_path)
            ui.message("Soubor s popisky otevřen v editoru.")
        else:
            ui.message("Soubor s popisky zatím neexistuje.")

    __gestures = {
        'kb:NVDA+control+l': 'prepareLabel',
        'kb:NVDA+control+shift+l': 'saveFromClipboard',
        'kb:NVDA+control+alt+a': 'appendFromClipboard',
        'kb:NVDA+control+alt+l': 'manageLabels',
        'kb:NVDA+alt+l': 'speakAdditionalInfo'
    }
