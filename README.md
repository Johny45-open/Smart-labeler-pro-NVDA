<div lang = "cs">

# SmartLabeler

SmartLabeler je inteligentní doplněk pro NVDA, který umožňuje uživatelům zpřístupnit i ty nejnáročnější aplikace tím, že dovoluje přiřadit vlastní popisky a doplňující informace k libovolným prvkům uživatelského rozhraní.

Doplněk je navržen tak, aby spolehlivě fungoval i v moderních a komplexních aplikacích (jako je Nastavení Windows 11), kde se standardní identifikace prvků často mění nebo selhává.

## Hlavní funkce

- **Vlastní popisky:** Uložte si srozumitelný název pro tlačítka bez popisků nebo prvky s nicneříkajícími technickými názvy.
- **Víceúrovňová nápověda:** Ke každému prvku můžete přiřadit seznam více informací (např. hlavní popis, klávesové zkratky a užitečné tipy).
- **Extrémně přesná identifikace:** Doplněk využívá "otisk" prvku založený na názvu aplikace, třídě okna, AutomationID, roli, názvu prvku a kompletní cestě v hierarchii rodičů. To zaručuje, že popisek patří pouze tomu jednomu konkrétnímu tlačítku.
- **Imunita vůči pohybu:** Popisky drží, i když okno posunete, změníte jeho velikost nebo rozlišení obrazovky.
- **Práce se schránkou:** Žádné nepřístupné dialogy. Popisky se pohodlně vkládají přímo ze schránky systému.

## Klávesové zkratky

| Zkratka | Akce |
| --- | --- |
| `NVDA+Ctrl+L` | **Označit prvek:** Připraví aktuálně zaměřený objekt pro uložení popisku. |
| `NVDA+Ctrl+Shift+L` | **Uložit ze schránky:** Vezme text ze schránky a uloží jej jako popisky pro označený prvek. (Více řádků ve schránce = více popisků). |
| `NVDA+Ctrl+Alt+A` | **Přidat informaci:** Okamžitě přidá aktuální obsah schránky jako další řádek (informaci) k aktuálnímu prvku. |
| `NVDA+Alt+L` | **Číst další informaci:** Cyklicky prochází a předčítá uložené popisky pro aktuální prvek. | 
| `NVDA+Ctrl+Alt+L` | **Správce popisků:** Otevře databázi popisků (`labels.json`) v Poznámkovém bloku pro ruční úpravy nebozálohu. |

## Použití

### Jak uložit první popisek:
1. Najedete na prvek, který chcete pojmenovat.
2. Stiskněte `NVDA+Ctrl+L` (NVDA oznámí přípravu).
3. Zkopírujte požadovaný text (např. z editoru nebo webu) do schránky (Ctrl+C).
4. Stiskněte `NVDA+Ctrl+Shift+L`. NVDA potvrdí uložení a přečte uložený text.

### Jak přidat další informace (např. zkratky):
1. Zkopírujte další text do schránky.
2. Na stejném prvku stiskněte `NVDA+Ctrl+Alt+A`.
3. Nová informace se připojí na konec seznamu.

### Jak popisky číst:
- Při každém přechodu fokusu na prvek NVDA automaticky přečte **pouze první (hlavní)** popisek.
- Pokud chcete slyšet další uložené informace (např. nápovědu ke zkratkám), stiskněte opakovaně `NVDA+Alt+L`.

## Ukládání a správa

Všechna data jsou uložena v souboru `labels.json` ve složce doplňku. Díky zkratce `NVDA+Ctrl+Alt+L` můžete tento soubor kdykoliv otevřít, popisky v něm hromadně přepisovat, mazat nebo si soubor zálohovat pro přenos na jiný počítač.

## Kompatibilita

- Minimální verze NVDA: `2023.1`
- Testováno s NVDA: `2026.1`
- Aktuální verze doplňku: `1.5`

## Vývoj a přispívání

Doplněk je vyvíjen s důrazem na maximální přístupnost a stabilitu v prostředí Windows 11. 

Hlavní logika: `globalPlugins/smartLabeler/__init__.py`  
Konfigurace: `manifest.ini`

---
*Vytvořeno pro komunitu uživatelů NVDA.*
