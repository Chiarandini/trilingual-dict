# Dictionary data licences

> **The MIT licence in [`LICENSE`](LICENSE) covers the source code of this
> project only. It does not cover the dictionary data, or any database file
> built from that data.** `LICENSE` is kept as unmodified MIT text so that
> automated licence detection recognises it; the data terms live here.

The dictionary data comes from three third-party projects, all under
share-alike terms. Those terms propagate into derivative works, which includes
any `dictionary.db` this project builds.

| Source | Content | Licence | Attribution required |
|---|---|---|---|
| [JMdict](https://www.edrdg.org/jmdict/j_jmdict.html) | Japanese-English entries, JLPT levels | CC BY-SA 3.0 | Electronic Dictionary Research and Development Group (EDRDG) |
| [CC-CEDICT](https://cc-cedict.org/) | Chinese-English entries, pinyin | CC BY-SA 4.0 | MDBG / CC-CEDICT contributors |
| [KANJIDIC2](https://www.edrdg.org/wiki/index.php/KANJIDIC_Project) | Kanji metadata, stroke counts | CC BY-SA 3.0 | EDRDG |

JMdict and KANJIDIC2 are the property of the EDRDG and are used in conformance
with the group's [licence](https://www.edrdg.org/edrdg/licence.html).

## What this means in practice

**Using the CLI, Neovim plugin, or web app for yourself:** nothing to do.

**Redistributing a built database** (shipping `dictionary.db`, publishing the
web app with data baked in, submitting the iOS app to the App Store): the
database is a derivative work of CC BY-SA data. You must

1. attribute the sources in the table above somewhere a user can find them,
2. license the database itself under the matching CC BY-SA terms, and
3. not add restrictions that conflict with share-alike.

The MIT licence on the code does not let you relicense the data. The two
licences apply to different parts of the same repository.

**Writing your own code against the schema:** that is just MIT code, no
obligation, as long as you do not ship their data with it.

## Attribution snippet

For a UI "about" screen or an app-store description:

> Dictionary data from JMdict and KANJIDIC2, property of the Electronic
> Dictionary Research and Development Group, used under CC BY-SA 3.0; and from
> CC-CEDICT, used under CC BY-SA 4.0.
