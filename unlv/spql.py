# py module for implementing SPARQLWrapper with UNLV requirements
#
import re

from SPARQLWrapper import SPARQLWrapper, JSON

wd_endpoint = "https://query.wikidata.org/sparql"
LOAD_BASE = """select ?topic ?topicLabel ?categoryLabel
where {
  {
   ?topic wdt:P485 wd:Q96156694 .
    ?topic wdt:P31 ?category .
  }  
UNION 
  {
    ?topic wdt:P485 wd:Q73644758 .
    ?topic wdt:P31 ?category .
  }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }  
}
ORDER BY ?categoryLabel
"""

UNLV_NETWORK = '''PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX bd: <http://www.bigdata.com/rdf#>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?item ?itemLabel ?itemDescription ?occupation ?occupationLabel ("CF0A2C" as ?rgb) ?image
WHERE {
  ?item wdt:P31 wd:Q5 ;
        wdt:P108 wd:Q2302311 ;
        wdt:P106 ?occupation .
  #?item wdt:P1416 wd:Q73644758 . # use to limit set by affiliation (i.e. UNLV Libraries Q73644758)
  #FILTER(?occupation != wd:Q1622272) # use to remove an occupation from the set
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
  OPTIONAL { ?item wdt:P18 ?image. }
}
LIMIT 50'''


def get_wd_query(query):
    # retrieves a list matrix of the UNLV base query as a dict.
    user_agent = 'PySparqlTest/0.0 (https://linkedin.com/andre_hulet; andrehulet@gmail.com)'
    sparql = SPARQLWrapper(wd_endpoint, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    the_set = sparql.query().convert()
    return the_set


def load_base(json_dict):
    # preps the LOAD_BASE query results for use in Django
    clean_result = []
    for r in json_dict["results"]["bindings"]:
        # base query includes topic (Q code), topic label, category label (typeof)
        topic = r.get("topic", {}).get("value")
        topic_split = re.split(r'/', topic)
        topic_key = topic_split.pop()
        topic_label = r.get("topicLabel", {}).get("value")
        categ_label = r.get("categoryLabel", {}).get("value")
        clean_result_row = [topic_key, topic_label, categ_label]
        clean_result.append(clean_result_row)

    return clean_result


def load_network(json_dict):
    # processes Darnelle's unlv network query in prep for visualization
    clean_result = []
    for r in json_dict["results"]["bindings"]:
        # base query includes topic (Q code), topic label, category label (typeof)
        item = r.get("item", {}).get("value")
        item_split = re.split(r'/', item)
        item_key = item_split.pop()
        item_label = r.get("itemLabel", {}).get("value")
        item_desc = r.get("itemDescription", {}).get("value")
        occupation = r.get('occupation', {}).get('value')
        occupation_split = re.split(r'/', occupation)
        occupation_key = occupation_split.pop()
        occupation_label = r.get("occupationLabel", {}).get("value")
        clean_result_row = [item_key, item_label, item_desc, occupation_key, occupation_label]
        clean_result.append(clean_result_row)

    return clean_result


def visualize_network(source_list):
    from pyvis.network import Network

    # create empty network
    unlv_net = Network()

    # get unique lists of humans and occupations.
    # note: assigning dups to a dict discards the dup.
    human_dict = {}
    occ_dict = {}
    for i in source_list:
        human_dict[i[0]] = i[1]
        occ_dict[i[3]] = i[4]

    # add human nodes
    for k, v in human_dict.items():
        # print(k + ': ' + v)
        unlv_net.add_node(k, v, shape='circle', color='#00BFFF')

    # occupation nodes
    for k, v in occ_dict.items():
        # print(k + ': ' + v)
        unlv_net.add_node(k, v, shape='ellipse', color='#FF0000')

    # add edges
    for e in source_list:
        unlv_net.add_edge(e[0], e[3])

    # finish configure and create HTML
    # unlv_net.path = '~/PycharmProjects/sparqlBuilder2'
    unlv_net.show_buttons()
    # unlv_net.template = '~/PycharmProjects/sparqlBuilder2/the_template.html'
    the_html = unlv_net.generate_html()
    # targ = open('~/PycharmProjects/sparqlBuilder2/new_net.html', 'w')
    # targ.write(the_html)
    # targ.close()
    print(the_html)


def load_item_detail(json_dict):
    clean_result = []
    for r in json_dict["results"]["bindings"]:
        # base query includes item (Q code) label, the property, English language prop value
        item = r.get("item", {}).get("value")
        item_code = re.split(r'/', item).pop()
        item_label = r.get("itemLabel", {}).get("value")
        prop = r.get("propLabel", {}).get("value")
        # prop_code = re.split(r'\/', prop).pop()
        val = r.get("oLabel_en", {}).get("value")
        clean_result_row = [item_code, item_label, prop, val]
        clean_result.append(clean_result_row)

    return clean_result


def query_item_detail(qvalue):
    # provides query of properties for a given wikidata Q code
    # TO D0: include values in ?oLabel_en that don't have eng language labels, e.g. numeric values
    qry_begin = 'select ?item ?itemLabel ?propLabel ?oLabel_en where {VALUES ?item {wd:'

    qry_end = '''}. ?item ?praw ?oraw . ?prop wikibase:directClaim ?praw . ?oraw rdfs:label ?oLabel_en . 
    FILTER(lang(?oLabel_en)='en') 
    SERVICE wikibase:label {bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en".}
    }'''
    return qry_begin + qvalue + qry_end
