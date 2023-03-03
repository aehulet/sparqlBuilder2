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
    # TODO: pop qcode from end of url, as with item
    clean_result = []
    for r in json_dict["results"]["bindings"]:
        # base query includes topic (Q code), topic label, category label (typeof)
        item = r.get("item", {}).get("value")
        item_split = re.split(r'/', item)
        item_key = item_split.pop()
        item_label = r.get("itemLabel", {}).get("value")
        item_desc = r.get("itemDescription", {}).get("value")
        occupation_key = r.get('occupation', {}).get('value')
        occupation_label = r.get("occupationLabel", {}).get("value")
        clean_result_row = [item_key, item_label, item_desc, occupation_key, occupation_label]
        clean_result.append(clean_result_row)

    return clean_result


def visualize_network(source_list):
    # TODO: not getting unique occupation list
    from pyvis.network import Network
    unlv_net = Network()
    unlv_net.barnes_hut()

    # get unique list of humans
    human_list = []
    curr_human = ''
    for i in source_list:
        if not i[1] == curr_human:
            human_list.append([i[0], i[1]])
            curr_human = i[1]
    print(human_list)

    # get unique list of occupations
    occ_list = []
    curr_occ = ''
    for o in source_list:
        if not o[4] == curr_occ:
            occ_list.append([o[3], o[4]])
            curr_occ = o[4]
    print(occ_list)

    # add human nodes
    for h in human_list:
        unlv_net.add_node(h[0], h[1], shape='circle')

    # occupation nodes
    for o in occ_list:
        unlv_net.add_node(o[0], o[1], shape='ellipse')

    # add edges
    for e in source_list:
        unlv_net.add_edge(e[0], e[3])
    # create html
    unlv_net.show('unlv_net.html', True)


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
