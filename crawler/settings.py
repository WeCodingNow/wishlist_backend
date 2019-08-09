crawler_settings = {
    'domain_name': 'obi.ru',
    'rps': 10,                       # default 1
    'fetchers': 5,                  # default 1
    'parser_publishers': 1,         # default 1
    'savers': 2,                    # default 1
    'visited_urls_max': 10000,         # default None
}

elastic_settings = {
    'elastic_host': 'elasticsearch',    # default localhost
    'elastic_port': 9200,           # default 9200
}

# elastic_settings = {
#     'elastic_host': 'localhost',    # default localhost
#     'elastic_port': 9200,           # default 9200
# }


rabbit_settings = {
    'host': 'rabbitmq',            # default localhost
    'port': 5672,                   # default 5672
}

# rabbit_settings = {
#     'host': 'localhost',            # default localhost
#     'port': 5672,                   # default 5672
# }


print(rabbit_settings)
