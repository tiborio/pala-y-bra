# Pala y Bra

A daily Spanish word game. Each day has three rounds; each round gives you a first and a last letter,
and you type Spanish words (4+ letters) that start and end with them. Longer words score more, rare
words (✦) score double, and every round has a points goal.

Play: https://tiborio.github.io/pala-y-bra/

*Pala y Bra es un juego diario de palabras en español: tres rondas, dos letras y la palabra que las une.*

## How it works

It is a static site (GitHub Pages): `index.html` plus JSON data files. There is no server and no build step for the page itself.

- Each pair of letters has one file, `data/<first>-<last>.json` (`ñ` is written as `0`). A file lists every valid word for that pair, split into bands:
  `c` common (top 10k by frequency), `m` known (10k-50k), `r` long tail, and `u`, the subset of `r` that is still **not** double points.
- A word is **rare (✦)** when its whole family (the base word and its inflected forms) has no word in the 50k frequency list.
  Points are `(length - 3)`, doubled for rare words.
- `data/manifest.json` holds each pair's goal and the season schedule. The three pairs of the day come from a deterministic
  schedule based on the day number since the season start, so everyone gets the same puzzle and nothing needs a server.
- `data/vetadas.json` lists proper nouns and demonyms, so the game can say *why* a word is refused.
- Progress and stats are stored in each player's browser (`localStorage`). Nothing is sent anywhere, except word reports (below).
- Accents are ignored. Proper nouns and demonyms of countries, cities and regions do not count, unless the word has a distinct ordinary meaning.

## Repository layout

```
index.html          the whole game (HTML, CSS and JS in one file)
favicon.svg, og.png icon and social preview image
LICENCIAS.md        data sources and licenses
data/               generated: pair files, manifest.json, vetadas.json (do not edit by hand)
vocabulary/         everything needed to regenerate data/
```

## Regenerating the data (`vocabulary/`)

Inputs in `vocabulary/`:

| File | Purpose |
|---|---|
| `palabras.txt` | base word list |
| `es_50k.txt` | word frequencies, used for the bands and for rarity |
| `lemas.txt` | form to base-word links (from Wiktionary), used for word families |
| `excluir.txt`, `excluir_cat.txt`, `mixtas_cat.txt`, `excluir_extra.txt` | proper nouns and demonyms to ban |
| `permitir.txt` | **allow-list**: ordinary words that were wrongly banned, and words approved from player reports |
| `seasons.json` | the pair schedule. Created on first run; **do not delete or change it after launch**, or the daily puzzles change |

To rebuild, run `python build.py` inside `vocabulary/`. It writes a fresh `data/` folder next to the script.
Copy that folder's contents over the repo's `data/` folder, then commit and push.
(`extraer*.js` are the one-off scripts that extract the exclusion lists and `lemas.txt` from the Wiktionary dump; you only need them to refresh those lists.)

### Adding a word that players say is missing

When a player types a word that is not in the dictionary, the game offers "¿Es válida? Avísame de «PALABRA»".
That sends the word to a Google Form and Sheet. To approve words: add them to `vocabulary/permitir.txt`, run `build.py`, copy `data/`, push.
A word in `permitir.txt` also stops being banned if it was wrongly flagged as a demonym or proper noun.

## Testing without touching the live puzzle

Open the game with these query strings (they use separate storage, so your real progress is not affected):

- `?fecha=2026-11-10` plays as if it were that date
- `?par=H-O,F-E,J-E` forces specific pairs (also available with `fecha`)

The page must be served over HTTP, for example `python -m http.server` in the repo root, then open `http://localhost:8000/`.

## Credits and licenses

Word data is derived from `an-array-of-spanish-words` (MIT), the Letterpress list (CC0), FrequencyWords (CC BY-SA 4.0)
and Wiktionary (CC BY-SA 4.0). The generated `data/` files are shared under **CC BY-SA 4.0**. Details in [LICENCIAS.md](LICENCIAS.md).
A license for the game's own code has not been chosen yet.
