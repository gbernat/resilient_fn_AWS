# -*- coding: utf-8 -*-

"""
Function implementation test.
Usage: resilient-circuits selftest -l fn_aws
"""

import logging
import botocore.exceptions
from fn_aws.util.helper import AWSHelper

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
log.addHandler(logging.StreamHandler())


def selftest_function(opts):
    """
    Test connection to AWS and credentials
    """
    success = 'failure'
    app_configs = opts.get("fn_aws", {})

    # Instansiate helper (which gets appconfigs from file)
    helper = AWSHelper(app_configs, '')
    
    # Create EC2 client
    ec2_client = helper.get_client('ec2', '')

    try:
        # Test
        ec2_client.describe_instances(InstanceIds=['i-11111111111111111'])
        success = 'success'
    except botocore.exceptions.ClientError as err:
        if err.response['Error']['Code'] == 'InvalidInstanceID.Malformed':
            success = 'success'
        else:
            log.error(err)

    return {
        "state": success
    } 