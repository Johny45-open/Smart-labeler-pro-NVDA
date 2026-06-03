<div lang = "cs">

# SmartLabeler

SmartLabeler je doplněk pro NVDA, který umožňuje uložit vlastní popisek k aktuálně zaměřenému prvku a nechat si ho automaticky přečíst při dalším přesunu fokusu na stejný prvek.

Doplněk je užitečný hlavně v aplikacích, kde mají některé ovládací prvky nejasný, chybějící nebo opakovaný název a NVDA z nich bez doplňku nepřečte dostatečně srozumitelnou informaci.

## Funkce

- uložení vlastního popisku pro aktuální prvek,
- načtení textu popisku ze schránky,
- automatické přečtení uloženého popisku při získání fokusu,
- přesnější identifikace prvků podle aplikace, role, názvu, hierarchie rodičů a pořadí mezi podobnými prvky,
- bezpečnější práce s prvky, které mají stejný název a stejný typ.

## Klávesové zkratky

| Zkratka | Akce |
| --- | --- |
| `NVDA+Ctrl+L` | Připraví aktuální prvek k pojmenování. |
| `NVDA+Ctrl+Shift+L` | Uloží text ze schránky jako popisek připraveného prvku. |

## Použití

1. Přesuňte fokus na prvek, který chcete popsat.
2. Stiskněte `NVDA+Ctrl+L`.
3. Zkopírujte požadovaný text popisku do schránky.
4. Stiskněte `NVDA+Ctrl+Shift+L`.
5. Při příštím zaměření stejného prvku NVDA přečte uložený popisek.

## Ukládání popisků

Popisky se ukládají do souboru `labels.json` ve složce doplňku:

```text
globalPlugins/smartLabeler/labels.json
```

Tento soubor se vytvoří automaticky při prvním uložení popisku.

## Identifikace prvků

SmartLabeler se snaží rozpoznat konkrétní prvek podle více vlastností najednou. Nepoužívá pouze název a typ prvku, protože to u moderních aplikací často nestačí. Do identifikace zahrnuje mimo jiné:

- název aplikace,
- roli prvku,
- název prvku,
- automation ID, pokud ho aplikace poskytuje,
- třídu a framework prvku,
- cestu přes rodičovské prvky,
- pořadí mezi podobnými sourozenci.

Poloha okna na obrazovce se do uloženého klíče nepoužívá, aby popisky nezmizely po přesunutí okna.

## Omezení

Některé aplikace neposkytují dostatek stabilních přístupnostních údajů. Pokud má více prvků stejný název, stejný typ a zároveň chybí technické identifikátory, nemusí být možné je vždy dokonale odlišit.

V takových případech může být potřeba popisek uložit znovu po změně struktury okna nebo po aktualizaci aplikace.

## Kompatibilita

- Minimální verze NVDA: `2023.1`
- Testováno s NVDA: `2026.1`
- Aktuální verze doplňku: `1.1`

## Instalace

1. Stáhněte soubor `SmartLabeler.nvda-addon`.
2. Otevřete ho v systému s nainstalovaným NVDA.
3. Potvrďte instalaci doplňku.
4. Restartujte NVDA.

## Vývoj

Hlavní kód doplňku je v souboru:

```text
globalPlugins/smartLabeler/__init__.py
```

Manifest doplňku je v souboru:

```text
manifest.ini
```

Pro rychlé ověření syntaxe lze použít:

```powershell
python -m py_compile .\globalPlugins\smartLabeler\__init__.py
```

## Licence

Licence zatím není určena. Před veřejným publikováním repozitáře je vhodné doplnit soubor `LICENSE`.
