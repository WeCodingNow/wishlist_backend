settings = {
    'secret': '4iig9l2SIc8Ju4ml7VpV',
    'query_params': ["user_id", "access_token"],
    'signature_param_name': "sign",
    'auth_queue_name': "auth_queue",
    'reg_queue_name': "reg_queue",
}

# rabbit_settings = {
#     'host': 'rabbitmq',             # default localhost
#     'port': 5672,                   # default 5672
# }

rabbit_settings = {
    'host': 'localhost',            # default localhost
    'port': 5672,                   # default 5672
}

# postgres_settings = {
#     'host': 'db',
#     'port': 5432,
# }

postgres_settings = {
    'host': 'localhost',
    'port': 5432,
}


elastic_settings = [{'host': 'elastic', 'port': 9200}]
