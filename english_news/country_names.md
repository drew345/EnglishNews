# Offline country-name filter data

country_names.json contains the unique name, official_name and common_name
fields from pycountry's ISO 3166-1 dataset (countries and territories), retrieved
2026-09-14 from:
https://raw.githubusercontent.com/pycountry/pycountry/main/src/pycountry/databases/iso3166-1.json

This is a checked-in factual name list, not a runtime dependency or download.
Common aliases are explicit in vocabulary.py. No automatic ISO two-letter
codes are included: ordinary words such as “in” and “us” should not be treated
as codes. Explicit USA/U.S./UK aliases are allowed; plain “US” is not.
Matching is whole-gloss, ignoring case, surrounding sentence punctuation and
repeated spaces. Generic descriptions, adjectives and country-containing
phrases are deliberately not matched. Literal “Turkey”/“Georgia” remain
ambiguous under this requested simple rule. Removed entries are audited.

country_names_ko.json uses Unicode CLDR Korean territory labels (including
short/variant forms), restricted to ISO 3166-1 codes from the same pycountry
dataset. Retrieved 2026-09-14; Unicode license is in CLDR-LICENSE.txt.
https://raw.githubusercontent.com/unicode-org/cldr-json/main/cldr-json/cldr-localenames-full/main/ko/territories.json

Korean matching checks the vocabulary entry's word field, not its explanatory
ko_def or narrative text. It is exact after the same normalization, with a
small explicit alias list in vocabulary.py (e.g. 호주, 터키). No particle removal
or substring matching: 태국 matches, 태국인 and 한국어 do not. Ambiguous words
such as 오만/수단 can also denote ordinary concepts; this simple requested
filter does not disambiguate their meaning. Continents and supranational groups
are excluded from the imported list. No network or LLM call occurs at runtime.
