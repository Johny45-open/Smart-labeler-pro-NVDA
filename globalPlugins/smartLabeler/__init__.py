import globalPluginHandler
import api
import ui
import wx
import json
import os
import logging
import re
from .dialogs import LabelManagerDialog  # OPRAVENO: Přidán chybějící import správce

# Konfigurace loggeru - bude logovat do NVDA logu
logger = logging.getLogger('nvda.smartLabeler')

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    def __init__(self):
        super(GlobalPlugin, self).__init__()
        self.data_path = os.path.join(os.path.dirname(__file__), 'labels.json')
        self.labels = self.load_labels()
        self.pending_key = None
        self.last_focused_key = None
        self.last_label_index = 0
        logger.info("SmartLabeler: Plugin initialized.")

    def load_labels(self):
        if os.path.exists(self.data_path):
            try:
                with open(self.data_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"SmartLabeler: Error loading labels: {e}")
                return {}
        return {}

    def save_labels(self, labels_to_save=None):
        try:
            data = labels_to_save if labels_to_save is not None else self.labels
            with open(self.data_path, 'w', encoding='utf-8') as f:
                if not data:
                    f.write('{}')
                    logger.info("SmartLabeler: All labels deleted, file emptied.")
                else:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                    logger.info(f"SmartLabeler: Labels saved. Current keys: {list(data.keys())}")
        except Exception as e:
            logger.error(f"SmartLabeler: Error saving labels: {e}")

    def _get_key(self, obj):
        def sanitize(text):
            return re.sub(r'\d+', '', str(text)).strip()

        logger.info(f"SmartLabeler: DEBUGGING _get_key for object {obj.name}:")
        raw_app_name = obj.appModule.appName if obj.appModule else 'unknown'
        raw_name = getattr(obj, 'name', '')
        raw_role = getattr(obj, 'role', '')
        raw_automation_id = getattr(obj, 'automationID', '')
        raw_uia_class = getattr(obj, 'UIAClassName', '')
        raw_window_class = getattr(obj, 'windowClassName', '')

        app_name = sanitize(raw_app_name)
        name = sanitize(raw_name)
        role = sanitize(raw_role)
        automation_id = sanitize(raw_automation_id)
        
        uia_class = sanitize(raw_uia_class)
        if not uia_class:
            uia_class = sanitize(raw_window_class)
        
        # OPRAVENO: Hlubší a detailnější hierarchie rodičů proti kolizím
        path = []
        p = obj.parent
        parent_level = 0
        while p and parent_level < 5:
            p_role = sanitize(getattr(p, 'role', ''))
            p_name = sanitize(getattr(p, 'name', ''))
            p_id = sanitize(getattr(p, 'automationID', ''))
            
            p_parts = [p_role]
            if p_id:
                p_parts.append(f"ID[{p_id}]")
            if p_name and p_name != name:
                p_parts.append(f"N({p_name})")
                
            parent_token = "-".join(p_parts)
            if parent_token:
                path.append(parent_token)
                
            p = p.parent
            parent_level += 1
            
        path_str = "->".join(path) 
        
        key = f'{app_name}:{uia_class}:{role}:{name}:{automation_id}:{path_str}'
        logger.info(f"SmartLabeler:   Final generated key: '{key}'")
        return re.sub(r'\d+', '', key)

    def event_gainFocus(self, obj, nextHandler):
        nextHandler()
        
        # OPRAVENO: Odstraněno neustálé čtení z disku. Data se berou bezpečně z self.labels v paměti.
        key = self._get_key(obj)
        
        logger.info(f"SmartLabeler: Focus gained on object. Key: '{key}'")
        
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
        """Příprava objektu pro pojmenování."""
        obj = api.getFocusObject()
        if not obj:
            ui.message('Nebylo možné získat fokus.')
            return
        self.pending_key = self._get_key(obj)
        logger.info(f"SmartLabeler: Prepared label for key: {self.pending_key}")
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