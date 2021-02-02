# -*- coding: utf-8 -*-

"""Generate a default configuration-file section for fn_aws"""


def config_section_data():
    """
    Produce add the default configuration section to app.config,
    for fn_aws when called by `resilient-circuits config [-c|-u]`
    """
    config_data = None

    config_data = u"""[fn_aws]
aws_access_key_id = AWS_ACCESS_KEY_ID
aws_secret_access_key = AWS_SECRET_ACCESS_KEY

# Optional, for containment process 2 SG are required
#sg_ec2_containment = sg-isolation-1,sg-isolation-2

#http_proxy = http://proxy:80
#https_proxy = http://proxy:80
"""

    return config_data
