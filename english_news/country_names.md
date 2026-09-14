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
