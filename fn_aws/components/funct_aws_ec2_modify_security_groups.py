# -*- coding: utf-8 -*-
# pragma pylint: disable=unused-argument, no-self-use
"""Function implementation"""

import logging
from resilient_circuits import ResilientComponent, function, handler, StatusMessage, FunctionResult, FunctionError
from fn_aws.util.helper import AWSHelper
import json

PACKAGE_NAME = "fn_aws"


class FunctionComponent(ResilientComponent):
    """Component that implements Resilient function 'aws_ec2_modify_security_groups''"""

    def __init__(self, opts):
        """constructor provides access to the configuration options"""
        super(FunctionComponent, self).__init__(opts)
        self.options = opts.get(PACKAGE_NAME, {})

    @handler("reload")
    def _reload(self, event, opts):
        """Configuration options have changed, save new values"""
        self.options = opts.get(PACKAGE_NAME, {})

    @function("aws_ec2_modify_security_groups")
    def _aws_ec2_modify_security_groups_function(self, event, *args, **kwargs):
        """Function: Replaces the Security Groups assigned to the Instance for those described in aws_security_groups (can be a list of security group Ids separated by comma)"""
        try:

            # Get the wf_instance_id of the workflow this Function was called in
            wf_instance_id = event.message["workflow_instance"]["workflow_instance_id"]

            yield StatusMessage("Starting 'aws_ec2_modify_security_groups' running in workflow '{0}'".format(wf_instance_id))

            # Get the function parameters:
            aws_security_groups = kwargs.get("aws_security_groups")  # text
            aws_resource_id = kwargs.get("aws_resource_id")  # text
            aws_region = kwargs.get("aws_region")  # text
            aws_access_key_name = kwargs.get("aws_access_key_name")  # text

            log = logging.getLogger(__name__)
            log.info("aws_security_groups: %s", aws_security_groups)
            log.info("aws_resource_id: %s", aws_resource_id)
            log.info("aws_region: %s", aws_region)
            log.info("aws_access_key_name: %s", aws_access_key_name)
            yield StatusMessage("Function Inputs OK")


            # Instansiate helper (which gets appconfigs from file)
            helper = AWSHelper(self.options, aws_access_key_name)    
            yield StatusMessage("Appconfig Settings OK")

            # Create EC2 client
            ec2_client = helper.get_client('ec2', aws_region)
            yield StatusMessage("EC2 Client created")


            # TODO Input either by sg id or name (add input select parameter "ids or names")
            # sg_id = ec2_client.describe_security_groups(Filters=[ {'Name': 'group-name', 'Values': ['name_of_sg']} ])['SecurityGroups'][0]['GroupId']

            
            ##############################################
            success = False

            # Validate aws_security_groups in case multiple values (must be a list)
            sgs = aws_security_groups.split(',')

            try:
                res = ec2_client.modify_instance_attribute(InstanceId=aws_resource_id, Groups=sgs)
                if res['ResponseMetadata']['HTTPStatusCode'] == 200:
                    log.info('Security Groups replaced.\n')
                    success = True
                else:
                    log.error('Cannot replace security groups.\n{}\n'.format(str(res)))

            except Exception as e:
                raise ValueError("Cannot replace security groups.\n Error: {0}".format(e))

            ##############################################

            yield StatusMessage("Finished 'aws_ec2_modify_security_groups' that was running in workflow '{0}'".format(wf_instance_id))

            results = {
                "success": success
            }

            # Produce a FunctionResult with the results
            yield FunctionResult(results)
        except Exception:
            yield FunctionError()
