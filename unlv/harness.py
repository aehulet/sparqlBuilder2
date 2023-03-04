def vis_harness():
    from . import spql
    dict = spql.get_wd_query(spql.UNLV_NETWORK)
    alist = spql.load_network(dict)
    spql.visualize_network(alist)
