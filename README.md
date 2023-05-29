# Data Source

| | Notes |
| --- | --- |
| **Content** | BHS(A) (Biblia Hebraica Stuttgartensia (Amstelodamensis)) |
| **Source** | <https://github.com/ETCBC/bhsa> |
| **Format** | Text-Fabric (<https://github.com/Dans-labs/text-fabric>) |
| **License** | CC BY-NC 4.0 |

## Content

### BHSA

BHS(A) (Biblia Hebraica Stuttgartensia (Amstelodamensis)).

> The text is based on the Biblia Hebraica Stuttgartensia edited by Karl Elliger and Wilhelm Rudolph, Fifth Revised Edition, edited by Adrian Schenker, © 1977 and 1997 Deutsche Bibelgesellschaft, Stuttgart.
> <https://etcbc.github.io/bhsa/>

The BHS is based on the WLC but where BHSA differs, the BHS is the base text. This source includes tagging for morphology and syntax. Ketivs are unpointed. Pointing and parsing is provided for Qeres.

### Import Notes

Right now, we lose "unknown"s from the ETCBC data by "null"ing them. This means that "unknown" gender, for example, ends up `null`. This is lossy and I'm not sure its implications.

### Enrichments:

 - Simple (Coarse) Genre Labels from Syntatic Variation Project (<https://github.com/ETCBC/genre_synvar/>)
 - Accent Data (name + disjunctive/conjunctive)
 - Semantic Domain
 - LXX Lexeme
 - ESV Lexeme? (cf. Tyndale Amalgamated work)
 - Parsing for Ketivs (Tyndale)

## To Build

You will need to use a version of node compatible with `better-sqlite3` but then it's just:

```
node ./main.js
```
