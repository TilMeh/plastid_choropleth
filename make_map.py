#####################
# IMPORT OPERATIONS #
#####################
import plotly.express as px
import argparse, logging, coloredlogs, os.path, math
import pandas as pd
from iso3166 import countries

###############
# AUTHOR INFO #
###############
__author__ = 'Michael Gruenstaeudl <m.gruenstaeudl@fu-berlin.de>, '\
			 'Tilman Mehl <tilmanmehl@zedat.fu-berlin.de>'
__copyright__ = 'Copyright (C) 2020 Michael Gruenstaeudl and Tilman Mehl'
__info__ = 'Create map of plastid genomes origins per country.'
__version__ = '2020.07.06.1300'


# Read translate dictionary
# Read country counts
# go through input
#   translate if possible
#   manually translate and append


def read_country_counts(fp_input):
    with open(fp_input) as fh_input:
        lines = fh_input.readlines()

    country_counts = {}
    corrections = False
    for line in lines:
        country = line.strip().split(" ",1)[1]
        count = line.strip().split(" ",1)[0]
        country_counts[country] = count

    return country_counts

def translate_countries(country_counts, fp_translate):
    trans_dict = read_translate_dict(fp_translate)
    cc_trans = {}
    correction = False
    for key in country_counts:
        if key in trans_dict:
            cc_trans[trans_dict[key]] = int(country_counts[key])
        else:
            correct_code = get_country_code(key)
            trans_dict[key] = correct_code
            cc_trans[trans_dict[key]] = int(country_counts[key])

    write_translate_dict(fp_translate, trans_dict)

    return cc_trans

def read_translate_dict(fp_translate):
    trans_dict = {}
    if os.path.isfile(fp_translate):
        with open(fp_translate,"r") as fh_translate:
            lines = fh_translate.readlines()
        for line in lines:
            splitline = line.strip().split("\t")
            trans_dict[splitline[0]] = splitline[1]

    return trans_dict

def write_translate_dict(fp_translate, trans_dict):
    with open(fp_translate,"w") as fh_translate:
        for k, v in trans_dict.items():
            fh_translate.write(str(k) + "\t" + str(v) + "\n")


def get_country_code(country):
    country_alpha3 = None
    try:
        country_alpha3 = countries.get(country).alpha3
    except Exception as err:
        code_ok = False
        corrections = True
        print("unable to resolve country " + country + "! Please provide the correct ISO-3166-alpha3 code for " + country)
        while not code_ok:
            country_alpha3 = input()
            try:
                country_alpha3 = countries.get(country_alpha3).alpha3
                code_ok = True
            except:
                print("Invalid ISO-3166-alpha3 code " + country_alpha3 + "! Please provide the correct ISO-3166-alpha3 code for " + country)
    return country_alpha3


def main(args):
    # Read in raw counts
    country_counts = read_country_counts(args.input)
    # Translate country names to valid ISO-3166-alpha3 codes
    cc_trans = translate_countries(country_counts, args.translate)
    # Convert dict to DataFrame
    map_data = pd.DataFrame(cc_trans.items(), columns=["iso_alpha", "genome_count"])
    if args.log_scale:
        counts_log = [math.log(x) for x in map_data["genome_count"]]
        map_data["genome_count"] = counts_log
    # Create map
    fig = px.choropleth(map_data, locations="iso_alpha", color="genome_count", hover_name=map_data.index, color_continuous_scale=px.colors.sequential.Plasma)
    fig.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="  --  ".join([__author__, __copyright__, __info__, __version__]))
    parser.add_argument("-i", "--input", type=str, required=True, help="path to input file")
    parser.add_argument("-t", "--translate", type=str, required=True, help="path to country code translation file")
    parser.add_argument("-l", "--log_scale", action="store_true", required=False, default=False, help="Use log scale on counts.")
    args = parser.parse_args()
    main(args)
