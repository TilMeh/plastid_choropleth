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
__version__ = '2020.07.07.1800'

#############
# DEBUGGING #
#############
import ipdb
#ipdb.set_trace()


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
            if trans_dict[key] in cc_trans:
                cc_trans[trans_dict[key]] += int(country_counts[key])
            else:
                cc_trans[trans_dict[key]] = int(country_counts[key])
        else:
            correct_code = get_country_code(key)
            trans_dict[key] = correct_code
            if trans_dict[key] in cc_trans:
                cc_trans[trans_dict[key]] += int(country_counts[key])
            else:
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
        print("unable to resolve country `%s`! Please provide the correct ISO-3166-alpha3 code for `%s`" % (country, country))
        while not code_ok:
            country_alpha3 = input()
            try:
                country_alpha3 = countries.get(country_alpha3).alpha3
                code_ok = True
            except:
                print("Invalid ISO-3166-alpha3 code `%s`! Please provide the correct ISO-3166-alpha3 code for `%s`" %(country_alpha3, country))
    return country_alpha3

def assign_categories(cc_trans):
    cc_categories = {}
    for k, v in cc_trans.items():
        if v > 100:
            cc_categories[k] = ">100"
        elif v < 100 and v >= 50:
            cc_categories[k] = "50-100"
        elif v < 50 and v >= 10:
            cc_categories[k] = "10-50"
        elif v < 10 and v >= 1:
            cc_categories[k] = "1-10"

    return cc_categories

def main(args):
    # Read in raw counts
    country_counts = read_country_counts(args.input)
    # Translate country names to valid ISO-3166-alpha3 codes
    cc_trans = translate_countries(country_counts, args.translate)
    # Assign categories
    cc_categories = assign_categories(cc_trans)
    # Convert dict to DataFrame
    #map_data = pd.DataFrame(cc_trans.items(), columns=["iso_alpha", "genome_count"])
    map_data = pd.DataFrame(cc_categories.items(), columns=["iso_alpha", "category"])
    cat_order = {"category": ["1-10", "10-50", "50-100", ">100"]}
    # Create map
    fig = px.choropleth(map_data,
						title='Distribution of sequenced plastid genomes by end of 2019',
                        locations="iso_alpha",
                        color="category",
                        category_orders=cat_order,
                        hover_name=map_data.index,
                        #color_continuous_scale=px.colors.sequential.Plasma
                        color_discrete_sequence=px.colors.sequential.Greys
                       )

    fig.update_geos(
		visible=False,
		showcountries=True,
		#countrycolor="grey",
		projection_type="mollweide"
	)

    #fig.write_html(args.output)
    fig.write_image(args.output)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="  --  ".join([__author__, __copyright__, __info__, __version__]))
    parser.add_argument("-i", "--input", type=str, required=True, help="path to input file")
    parser.add_argument("-o", "--output", type=str, required=True, help="path to output svg file")
    parser.add_argument("-t", "--translate", type=str, required=True, help="path to country code translation file")
    args = parser.parse_args()
    main(args)
