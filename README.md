plastid_choropleth
==================
Displays a world map with counts of sequenced plastid genomes for species originating from each country.

## USAGE
#### Map with summary variable in normal scale
```
$ python3 make_map.py -i example/records_per_country.txt -t example/translate_file.txt -o example/map.html
```

#### Map with summary variable in log-scale (option `-l/--log_scale`)
```
$ python3 make_map.py -i example/records_per_country.txt -t example/translate_file.txt -l -o example/map_log.html
```

## NOTES
Concerning input data:
The map requires ISO-3166 country names/codes, but the country names provided in the plastid genome entries sometimes don't match that.
The script offers a primitive translation functionality. If an unknown country name is encountered, the ISO-3166 3-digit code (alpha3) can be entered manually and the assignment is saved in the translation file for future cases.
Data has to be provided in format "Counts Country". One country per line.
