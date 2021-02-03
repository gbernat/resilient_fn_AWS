# -*- coding: utf-8 -*-
# pragma pylint: disable=unused-argument, no-self-use
"""Function implementation"""

import logging
from resilient_circuits import ResilientComponent, function, handler, StatusMessage, FunctionResult, FunctionError
from fn_aws.util.helper import AWSHelper
import json

PACKAGE_NAME = "fn_aws"


class FunctionComponent(ResilientComponent):
    """Component that implements Resilient function 'aws_ec2_describe_instance''"""

    def __init__(self, opts):
        """constructor provides access to the configuration options"""
        super(FunctionComponent, self).__init__(opts)
        self.options = opts.get(PACKAGE_NAME, {})

    @handler("reload")
    def _reload(self, event, opts):
        """Configuration options have changed, save new values"""
        self.options = opts.get(PACKAGE_NAME, {})

    @function("aws_ec2_describe_instance")
    def _aws_ec2_describe_instance_function(self, event, *args, **kwargs):
        """Function: None"""
        try:

            # Get the wf_instance_id of the workflow this Function was called in
            wf_instance_id = event.message["workflow_instance"]["workflow_instance_id"]

            yield StatusMessage("Starting 'aws_ec2_describe_instance' running in workflow '{0}'".format(wf_instance_id))

            # Get the function parameters:
            aws_resource_id = kwargs.get("aws_resource_id")  # text
            aws_region = kwargs.get("aws_region")  # text

            log = logging.getLogger(__name__)
            log.info("aws_resource_id: %s", aws_resource_id)
            log.info("aws_region: %s", aws_region)
            yield StatusMessage("Function Inputs OK")


            # Instansiate helper (which gets appconfigs from file)
            helper = AWSHelper(self.options)    
            yield StatusMessage("Appconfig Settings OK")

            # Create EC2 client
            ec2_client = helper.get_client('ec2', aws_region)
            yield StatusMessage("EC2 Client created")


            ##############################################
            success = False
            res_json = {}
            try:
                res = ec2_client.describe_instances(InstanceIds=[aws_resource_id])
                if res['ResponseMetadata']['HTTPStatusCode'] == 200:
                    #pd = res['Reservations'][0]['Instances'][0]

                    res_json = json.loads(json.dumps(res['Reservations'][0], default=str))
                    success = True
                else:
                    log.error('[ERROR] {}'.format(str(res)))

            except Exception as e:
                raise ValueError("Cannot get describe_instance.\n Error: {0}".format(e))
            
            ##############################################

            yield StatusMessage("Finished 'aws_ec2_describe_instance' that was running in workflow '{0}'".format(wf_instance_id))

            results = {
                "success": success,
                "reservations": res_json
            }

            # Produce a FunctionResult with the results
            yield FunctionResult(results)
        except Exception:
            yield FunctionError()
