# -*- coding: utf-8 -*-

"""Generate a default configuration-file section for fn_aws"""


def config_section_data():
    """
    Produce add the default configuration section to app.config,
    for fn_aws when called by `resilient-circuits config [-c|-u]`
    """
    config_data = None

    config_data = u"""[fn_aws]
# Default AWS credentials to be used if no other is indicated in funtion's field 'aws_access_key_name'
aws_access_key_id = AWS_ACCESS_KEY_ID
aws_secret_access_key = AWS_SECRET_ACCESS_KEY

# You can use different access_key/secret_access_key pairs as this (avoid '<' and '>', and add '_' after your name):
# <powerful-key-name>_aws_access_key_id = AWS_ACCESS_KEY_ID
# <powerful-key-name>_aws_secret_access_key = AWS_SECRET_ACCESS_KEY
# To use these credentials in workflows, enter 'powerful-key-name' in field 'aws_access_key_name', otherwise default credentials will be used.

# Default region name to be used when not explicitly indicated in functions
default_region = sa-east-1

#http_proxy = http://proxy:80
#https_proxy = http://proxy:80
"""

    return config_data
