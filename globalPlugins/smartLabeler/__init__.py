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
        parent_name = getattr(obj.parent, 'name', 'no_parent') if obj.parent else 'no_parent'
        index = self._get_obj_index(obj)
        return f'{app_name}:{automation_id}:{role}:{name}:{parent_name}:{index}'

    def event_gainFocus(self, obj, nextHandler):
        nextHandler()
        # Vždy načteme nejaktuálnější stav souboru, kdyby jej uživatel upravil v editoru
        self.labels = self.load_labels()
        key = self._get_key(obj)
        if key in self.labels:
            ui.message(self.labels[key])
    
    def script_prepareLabel(self, gesture):
        obj = api.getFocusObject()
        if not obj:
            ui.message('Nebylo možné získat fokus.')
            return
        self.pending_key = self._get_key(obj)
        ui.message('Objekt připraven k pojmenování. Zkopírujte text do schránky a stiskněte NVDA+Ctrl+Shift+L pro uložení.')

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
                    self.labels[self.pending_key] = text
                    self.save_labels()
                    ui.message(f'Popisek uložen: {text}')
                else:
                    ui.message('Schránka je prázdná.')
            else:
                ui.message('Nepodařilo se přečíst schránku.')
        else:
            ui.message('Nepodařilo se otevřít schránku.')
        self.pending_key = None
    
    def script_manageLabels(self, gesture):
        """Otevře soubor s popisky v textovém editoru."""
        if os.path.exists(self.data_path):
            os.startfile(self.data_path)
            ui.message("Soubor s popisky otevřen v editoru.")
        else:
            ui.message("Soubor s popisky zatím neexistuje.")

    __gestures = {
        'kb:NVDA+control+l': 'prepareLabel',
        'kb:NVDA+control+shift+l': 'saveFromClipboard',
        'kb:NVDA+control+alt+l': 'manageLabels'
    }
