import globalPluginHandler
import api
import ui
import wx
import json
import os

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

    def _to_text(self, value):
        if value is None:
            return ''
        try:
            return str(value)
        except:
            return ''

    def _get_attr(self, obj, attr, default=''):
        try:
            value = getattr(obj, attr)
        except:
            return default
        if value is None:
            return default
        return value

    def _get_uia_attr(self, obj, attr, default=''):
        try:
            element = getattr(obj, 'UIAElement', None)
        except:
            return default
        if not element:
            return default
        try:
            value = getattr(element, attr)
        except:
            return default
        if value is None:
            return default
        return value

    def _get_automation_id(self, obj):
        automation_id = self._get_attr(obj, 'automationID', '')
        if automation_id:
            return self._to_text(automation_id)
        return self._to_text(self._get_uia_attr(obj, 'cachedAutomationID', ''))

    def _get_class_name(self, obj):
        class_name = self._get_attr(obj, 'windowClassName', '')
        if class_name:
            return self._to_text(class_name)
        return self._to_text(self._get_uia_attr(obj, 'cachedClassName', ''))

    def _get_raw_obj_index(self, obj):
        try:
            index = obj.indexInParent
        except:
            return None
        if index is None:
            return None
        return index

    def _get_obj_index(self, obj):
        index = self._get_raw_obj_index(obj)
        if index is not None:
            return index
        sibling_index = self._get_sibling_index(obj)
        if sibling_index is not None:
            return sibling_index
        return ''

    def _get_children(self, obj):
        if not obj:
            return []
        try:
            children = obj.children
        except:
            return []
        if not children:
            return []
        try:
            return list(children)
        except:
            return []

    def _get_location_tuple(self, obj):
        location = self._get_attr(obj, 'location', None)
        if not location:
            return ''
        values = []
        for attr in ('left', 'top', 'width', 'height'):
            try:
                values.append(int(getattr(location, attr)))
            except:
                return self._to_text(location)
        return values

    def _get_root_location_tuple(self, obj):
        current = obj
        last = obj
        for _ in range(12):
            parent = self._get_attr(current, 'parent', None)
            if not parent:
                break
            last = parent
            current = parent
        return self._get_location_tuple(last)

    def _get_relative_location_tuple(self, obj):
        location = self._get_location_tuple(obj)
        root_location = self._get_root_location_tuple(obj)
        if (
            isinstance(location, list)
            and isinstance(root_location, list)
            and len(location) == 4
            and len(root_location) == 4
        ):
            return [
                location[0] - root_location[0],
                location[1] - root_location[1],
                location[2],
                location[3],
            ]
        return location

    def _get_sibling_signature(self, obj):
        return (
            self._to_text(self._get_attr(obj, 'role', '')),
            self._to_text(self._get_attr(obj, 'name', '')),
            self._get_automation_id(obj),
            self._get_class_name(obj),
            self._to_text(self._get_attr(obj, 'windowControlID', '')),
            self._to_text(self._get_uia_attr(obj, 'cachedFrameworkID', '')),
        )

    def _get_identity_signature(self, obj):
        return (
            self._get_sibling_signature(obj),
            self._get_raw_obj_index(obj),
            self._get_relative_location_tuple(obj),
        )

    def _is_same_object(self, first, second):
        if first is second:
            return True
        try:
            if first == second:
                return True
        except:
            pass
        return self._get_identity_signature(first) == self._get_identity_signature(second)

    def _get_sibling_index(self, obj):
        parent = self._get_attr(obj, 'parent', None)
        children = self._get_children(parent)
        if not children:
            return None
        for index, child in enumerate(children):
            if self._is_same_object(child, obj):
                return index
        return None

    def _get_same_sibling_ordinal(self, obj):
        parent = self._get_attr(obj, 'parent', None)
        children = self._get_children(parent)
        if not children:
            return ''
        target_signature = self._get_sibling_signature(obj)
        ordinal = 0
        for child in children:
            if self._get_sibling_signature(child) != target_signature:
                continue
            if self._is_same_object(child, obj):
                return ordinal
            ordinal += 1
        return ''

    def _get_position_info(self, obj):
        info = self._get_attr(obj, 'positionInfo', None)
        if not info:
            return ''
        try:
            return {self._to_text(key): self._to_text(value) for key, value in dict(info).items()}
        except:
            return self._to_text(info)

    def _get_obj_part(self, obj, include_location=False):
        sibling_index = self._get_sibling_index(obj)
        part = {
            'automationID': self._get_automation_id(obj),
            'className': self._get_class_name(obj),
            'controlID': self._to_text(self._get_attr(obj, 'windowControlID', '')),
            'frameworkID': self._to_text(self._get_uia_attr(obj, 'cachedFrameworkID', '')),
            'index': self._to_text(self._get_obj_index(obj)),
            'name': self._to_text(self._get_attr(obj, 'name', '')),
            'positionInfo': self._get_position_info(obj),
            'role': self._to_text(self._get_attr(obj, 'role', '')),
            'sameSiblingOrdinal': self._to_text(self._get_same_sibling_ordinal(obj)),
            'siblingIndex': self._to_text(sibling_index) if sibling_index is not None else '',
        }
        if include_location:
            part['location'] = self._get_relative_location_tuple(obj)
        return part

    def _get_parent_path(self, obj):
        path = []
        current = self._get_attr(obj, 'parent', None)
        for _ in range(8):
            if not current:
                break
            path.append(self._get_obj_part(current))
            current = self._get_attr(current, 'parent', None)
        path.reverse()
        return path

    def _get_key_data(self, obj, include_location=False):
        try:
            app_name = obj.appModule.appName if obj.appModule else 'unknown'
        except:
            app_name = 'unknown'
        return {
            'appName': self._to_text(app_name),
            'object': self._get_obj_part(obj, include_location=include_location),
            'parentPath': self._get_parent_path(obj),
        }

    def _dump_key(self, key):
        return 'v2:' + json.dumps(key, ensure_ascii=False, sort_keys=True, separators=(',', ':'))

    def _get_key(self, obj):
        return self._dump_key(self._get_key_data(obj))

    def _strip_location_from_key(self, key):
        try:
            obj_part = key.get('object', {})
        except:
            return key
        if isinstance(obj_part, dict):
            obj_part.pop('location', None)
        return key

    def _get_location_compatible_label(self, key, key_data):
        matches = []
        for stored_key, label in list(self.labels.items()):
            if not stored_key.startswith('v2:'):
                continue
            try:
                stored_key_data = json.loads(stored_key[3:])
            except:
                continue
            if self._strip_location_from_key(stored_key_data) == key_data:
                matches.append(label)
        if not matches:
            return None
        first_label = matches[0]
        for label in matches:
            if label != first_label:
                return None
        self.labels[key] = first_label
        try:
            self.save_labels()
        except:
            pass
        return first_label

    def _get_legacy_key(self, obj):
        try:
            app_name = obj.appModule.appName if obj.appModule else 'unknown'
        except:
            app_name = 'unknown'
        automation_id = self._get_attr(obj, 'automationID', '')
        role = self._get_attr(obj, 'role', '')
        name = self._get_attr(obj, 'name', '')
        parent = self._get_attr(obj, 'parent', None)
        parent_name = self._get_attr(parent, 'name', 'no_parent') if parent else 'no_parent'
        index = self._get_raw_obj_index(obj)
        if index is None:
            index = 0
        return f'{app_name}:{automation_id}:{role}:{name}:{parent_name}:{index}'

    def _legacy_key_is_safe(self, obj):
        return bool(self._get_automation_id(obj))

    def event_gainFocus(self, obj, nextHandler):
        nextHandler()
        key_data = self._get_key_data(obj)
        key = self._dump_key(key_data)
        label = self.labels.get(key)
        if label is None:
            label = self._get_location_compatible_label(key, key_data)
        if label is None:
            legacy_key = self._get_legacy_key(obj)
            if legacy_key in self.labels and self._legacy_key_is_safe(obj):
                label = self.labels[legacy_key]
        if label:
            ui.message(label)
    
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
    
    __gestures = {
        'kb:NVDA+control+l': 'prepareLabel',
        'kb:NVDA+control+shift+l': 'saveFromClipboard'
    }
