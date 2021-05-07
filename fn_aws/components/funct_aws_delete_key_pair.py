# -*- coding: utf-8 -*-
# pragma pylint: disable=unused-argument, no-self-use
"""Function implementation"""

import logging
import json
from resilient_circuits import ResilientComponent, function, handler, StatusMessage, FunctionResult, FunctionError
from fn_aws.util.helper import AWSHelper

PACKAGE_NAME = "fn_aws"


class FunctionComponent(ResilientComponent):
    """Component that implements Resilient function 'aws_delete_key_pair''"""

    def __init__(self, opts):
        """constructor provides access to the configuration options"""
        super(FunctionComponent, self).__init__(opts)
        self.options = opts.get(PACKAGE_NAME, {})

    @handler("reload")
    def _reload(self, event, opts):
        """Configuration options have changed, save new values"""
        self.options = opts.get(PACKAGE_NAME, {})

    @function("aws_delete_key_pair")
    def _aws_delete_key_pair_function(self, event, *args, **kwargs):
        """Function: None"""
        try:

            # Get the wf_instance_id of the workflow this Function was called in
            wf_instance_id = event.message["workflow_instance"]["workflow_instance_id"]

            yield StatusMessage("Starting 'aws_delete_key_pair' running in workflow '{0}'".format(wf_instance_id))

            # Get the function parameters:
            aws_region = kwargs.get("aws_region")  # text
            aws_key_name = kwargs.get("aws_key_name")  # text
            aws_access_key_name = kwargs.get("aws_access_key_name")  # text

            log = logging.getLogger(__name__)
            log.info("aws_region: %s", aws_region)
            log.info("aws_key_name: %s", aws_key_name)
            log.info("aws_access_key_name: %s", aws_access_key_name)
            yield StatusMessage("Function Inputs OK")


            # Instansiate helper (which gets appconfigs from file)
            helper = AWSHelper(self.options, aws_access_key_name)
            yield StatusMessage("Appconfig Settings OK")

            # Create EC2 client
            ec2_client = helper.get_client('ec2', aws_region)
            yield StatusMessage("EC2 Client created")


            ##############################################
            success = False
            res_json = {}

            try:
                # First query for previous key pair data for function return
                res = ec2_client.describe_key_pairs(KeyNames=[aws_key_name])
                if res['ResponseMetadata']['HTTPStatusCode'] == 200:
                    res_json = json.loads(json.dumps(res['KeyPairs'][0], default=str))

                    log.info('Deleting key pair...')
                    # Delete key pair
                    res = ec2_client.delete_key_pair(KeyName=aws_key_name)
                    if res['ResponseMetadata']['HTTPStatusCode'] == 200:
                        success = True
                    else:
                        log.error("Cannot delete kay pair.\n Error: {0}".format(str(res)))
                else:
                    log.error("Cannot get describe_key_pairs.\n Error: {0}".format(str(res)))

            except Exception as e:
                raise ValueError("Cannot delete key pair.\n Error: {0}".format(e))

            ##############################################

            yield StatusMessage("Finished 'aws_delete_key_pair' that was running in workflow '{0}'".format(wf_instance_id))

            results = {
                "success": success,
                "deletedKeyPair": res_json
            }

            # Produce a FunctionResult with the results
            yield FunctionResult(results)
        except Exception:
            yield FunctionError()
