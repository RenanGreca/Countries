import requests
import json
import xmltodict
import os
import sys
import codecs
import io

import argparse

parser = argparse.ArgumentParser(description='''Translates a JSON of countries using Bing API.''')
parser.add_argument('-s', '--source', type=str, required=True,
                    help='''Source language (two-character code)''')
parser.add_argument('-t', '--target', type=str, required=True,
                    help='''Target language (two-character code)''')
    
directory = os.path.dirname(os.path.realpath(__file__))
json_path = os.path.join(directory, 'json') 
out_path = os.path.join(directory, 'countries')
countries = json.load(open(os.path.join(json_path, 'countries.json'), 'r'))

# Gets client ID and Secret from external files
with open(os.path.join(directory, 'client_id.txt'), 'r') as client_id_file:
    client_id = client_id_file.readlines()[0]
with open(os.path.join(directory, 'client_secret.txt'), 'r') as client_secret_file:
    client_secret = client_secret_file.readlines()[0]

def main(args):
    t = args.target
    s = args.source

    # Get access token from Microsoft
    print "Acquiring Access Token."

    url = "https://datamarket.accesscontrol.windows.net/v2/OAuth2-13"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    body = "grant_type=client_credentials&client_id="+client_id+"&client_secret="+client_secret+"&scope=http://api.microsofttranslator.com"
    r = requests.post(url, headers=headers, data=body)
    auth = json.loads(r.text)

    print "Starting translation."
    tcountries = []
    for country in countries:
        # Get original name from JSON
        name = country["name"]
        code = country["code"]

        sys.stdout.write("\rTranslating... %s" % name)
        sys.stdout.flush()

        # Translate the country's name from API
        url = "http://api.microsofttranslator.com/v2/Http.svc/Translate?text="+name+"&from="+s+"&to="+t
        headers = {"Authorization": "Bearer "+auth['access_token']}
        r = requests.get(url, headers=headers)

        root = xmltodict.parse(r.text)
        tcountries.append({'name': root['string']['#text'], 'code': code})


    # Saves translated names into new JSON
    print "Saving to file."

    # OMG Python character encoding is garbage
    data = json.dumps(tcountries, ensure_ascii=False, encoding='utf8')
    with io.open(os.path.join(out_path, t+'.json'), 'w', encoding='utf8') as json_file:
        json_file.write(data)

if __name__ == '__main__':
    args = parser.parse_args()
    main(args)

