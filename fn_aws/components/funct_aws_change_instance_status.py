# -*- coding: utf-8 -*-
# pragma pylint: disable=unused-argument, no-self-use
"""Function implementation"""

import logging
from resilient_circuits import ResilientComponent, function, handler, StatusMessage, FunctionResult, FunctionError
from fn_aws.util.helper import AWSHelper
import json

PACKAGE_NAME = "fn_aws"


class FunctionComponent(ResilientComponent):
    """Component that implements Resilient function 'aws_change_instance_status''"""

    def __init__(self, opts):
        """constructor provides access to the configuration options"""
        super(FunctionComponent, self).__init__(opts)
        self.options = opts.get(PACKAGE_NAME, {})

    @handler("reload")
    def _reload(self, event, opts):
        """Configuration options have changed, save new values"""
        self.options = opts.get(PACKAGE_NAME, {})

    @function("aws_change_instance_status")
    def _aws_change_instance_status_function(self, event, *args, **kwargs):
        """Function: None"""
        try:

            # Get the wf_instance_id of the workflow this Function was called in
            wf_instance_id = event.message["workflow_instance"]["workflow_instance_id"]

            yield StatusMessage("Starting 'aws_change_instance_status' running in workflow '{0}'".format(wf_instance_id))

            # Get the function parameters:
            aws_instance_status = self.get_select_param(kwargs.get("aws_instance_status"))  # select, values: "start", "stop", "hibernate", "terminate"
            aws_resource_id = kwargs.get("aws_resource_id")  # text
            aws_region = kwargs.get("aws_region")  # text

            log = logging.getLogger(__name__)
            log.info("aws_instance_status: %s", aws_instance_status)
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

            # Validate aws_resource_id in case multiple values (must be a list)
            resources = aws_resource_id.split(',')

            try:
                if aws_instance_status == 'hibernate' or aws_instance_status == 'stop':
                    # If hibernate is selected but the instance cannot hibernate successfully, a normal shutdown occurs
                    res = ec2_client.stop_instances(InstanceIds=resources, Hibernate= (True if aws_instance_status=='hibernate' else False))
                elif aws_instance_status == 'start':
                    res = ec2_client.start_instances(InstanceIds=resources)
                elif aws_instance_status == 'terminate':
                    res = ec2_client.terminate_instances(InstanceIds=resources)
                else:
                    raise ValueError("Status not allowed.\n")

                if res['ResponseMetadata']['HTTPStatusCode'] == 200:

                    res_json = json.loads(json.dumps(res, default=str))
                    success = True
                else:
                    log.error('Cannot change instances status.\n{}\n'.format(str(res)))

            except Exception as e:
                raise ValueError("Cannot change instances status.\n Error: {0}".format(e))

            ##############################################

            yield StatusMessage("Finished 'aws_change_instance_status' that was running in workflow '{0}'".format(wf_instance_id))

            results = {
                "success": success,
                "statusInstances": res_json
            }

            # Produce a FunctionResult with the results
            yield FunctionResult(results)
        except Exception:
            yield FunctionError()
