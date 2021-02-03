# -*- coding: utf-8 -*-
# pragma pylint: disable=unused-argument, no-self-use
"""Function implementation"""

import logging
from resilient_circuits import ResilientComponent, function, handler, StatusMessage, FunctionResult, FunctionError
from fn_aws.util.helper import AWSHelper
import json

PACKAGE_NAME = "fn_aws"


class FunctionComponent(ResilientComponent):
    """Component that implements Resilient function 'aws_create_tags''"""

    def __init__(self, opts):
        """constructor provides access to the configuration options"""
        super(FunctionComponent, self).__init__(opts)
        self.options = opts.get(PACKAGE_NAME, {})

    @handler("reload")
    def _reload(self, event, opts):
        """Configuration options have changed, save new values"""
        self.options = opts.get(PACKAGE_NAME, {})

    @function("aws_create_tags")
    def _aws_create_tags_function(self, event, *args, **kwargs):
        """Function: Assign Tags to resources"""
        try:

            # Get the wf_instance_id of the workflow this Function was called in
            wf_instance_id = event.message["workflow_instance"]["workflow_instance_id"]

            yield StatusMessage("Starting 'aws_create_tags' running in workflow '{0}'".format(wf_instance_id))

            # Get the function parameters:
            aws_resource_id = kwargs.get("aws_resource_id")  # text
            aws_region = kwargs.get("aws_region")  # text
            aws_tag_names = kwargs.get("aws_tag_names")  # text
            aws_access_key_name = kwargs.get("aws_access_key_name")  # text

            log = logging.getLogger(__name__)
            log.info("aws_resource_id: %s", aws_resource_id)
            log.info("aws_region: %s", aws_region)
            log.info("aws_tag_names: %s", aws_tag_names)
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

            # Validate aws_tag_names format
            try:
                tags = json.loads(aws_tag_names.replace("'",'"').replace(' ',''))
                if type(tags) is not list:
                    raise ValueError("Illegal format for aws_tag_names.\n")
                for tag in tags:
                    if type(tag) is not dict:
                        raise ValueError("Illegal format for aws_tag_names.\n")
            except Exception as e:
                raise ValueError("Illegal format for aws_tag_names.\n Error: {0}".format(e))

            # Validate aws_resource_id in case multiple values (must be a list)
            resources = aws_resource_id.split(',')

            try:
                res = ec2_client.create_tags(Resources=resources, Tags=tags)
                if res['ResponseMetadata']['HTTPStatusCode'] == 200:
                    success = True
                else:
                    log.error('[ERROR] {}'.format(str(res)))
            except Exception as e:
                raise ValueError("Cannot tag resource.\n Error: {0}".format(e))
            
            ##############################################

            yield StatusMessage("Finished 'aws_create_tags' that was running in workflow '{0}'".format(wf_instance_id))

            results = {
                "success": success
            }

            # Produce a FunctionResult with the results
            yield FunctionResult(results)
        except Exception:
            yield FunctionError()
