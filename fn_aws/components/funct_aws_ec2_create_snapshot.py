# -*- coding: utf-8 -*-
# pragma pylint: disable=unused-argument, no-self-use
"""Function implementation"""

import logging
from resilient_circuits import ResilientComponent, function, handler, StatusMessage, FunctionResult, FunctionError
from fn_aws.util.helper import AWSHelper
import json

PACKAGE_NAME = "fn_aws"


class FunctionComponent(ResilientComponent):
    """Component that implements Resilient function 'aws_ec2_create_snapshot''"""

    def __init__(self, opts):
        """constructor provides access to the configuration options"""
        super(FunctionComponent, self).__init__(opts)
        self.options = opts.get(PACKAGE_NAME, {})

    @handler("reload")
    def _reload(self, event, opts):
        """Configuration options have changed, save new values"""
        self.options = opts.get(PACKAGE_NAME, {})

    @function("aws_ec2_create_snapshot")
    def _aws_ec2_create_snapshot_function(self, event, *args, **kwargs):
        """Function: None"""
        try:

            # Get the wf_instance_id of the workflow this Function was called in
            wf_instance_id = event.message["workflow_instance"]["workflow_instance_id"]

            yield StatusMessage("Starting 'aws_ec2_create_snapshot' running in workflow '{0}'".format(wf_instance_id))

            # Get the function parameters:
            aws_resource_id = kwargs.get("aws_resource_id")  # text
            aws_region = kwargs.get("aws_region")  # text
            aws_access_key_name = kwargs.get("aws_access_key_name")  # text

            log = logging.getLogger(__name__)
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


            ##############################################
            success = False
            res_json = ''

            # Get type of snapshot
            if aws_resource_id[:4] == 'vol-':
                do_ami_snapshot = False
            elif aws_resource_id[:2] == 'i-':
                do_ami_snapshot = True
            else:
                raise ValueError("Resource not allowed for snapshot.\n")

            if do_ami_snapshot:
                # Create AMI of Instance. This process creates also EBS snapshot
                log.info('Creating AMI from instance id: {}...'.format(aws_resource_id))
                try:
                    res = ec2_client.create_image(InstanceId=aws_resource_id, NoReboot=True, Name="resilient_ami_snapshot_from_"+aws_resource_id)
                    if res['ResponseMetadata']['HTTPStatusCode'] == 200:
                        res_json = res['ImageId']
                        success = True
                    else:
                        log.error('Cannot create AMI snapshot.\n{}\n'.format(str(res)))
                except Exception as e:
                    raise ValueError("Cannot create AMI snapshot.\n Error: {0}".format(e))

            else:
                # Only take EBS Snapshot
                log.info('Creating EBS snapshot...')
                try:
                    res = ec2_client.create_snapshot(VolumeId=aws_resource_id, Description="resilient_vol_snapshot_from_"+aws_resource_id)
                    if res['ResponseMetadata']['HTTPStatusCode'] == 200:
                        res_json = res['SnapshotId']
                        success = True
                    else:
                        log.error('Cannot create Volume snapshot.\n{}\n'.format(str(res)))
                except Exception as e:
                    raise ValueError("Cannot create Volume snapshot.\n Error: {0}".format(e))

            ##############################################

            yield StatusMessage("Finished 'aws_ec2_create_snapshot' that was running in workflow '{0}'".format(wf_instance_id))

            results = {
                "success": success,
                "snapshotId": res_json
            }

            # Produce a FunctionResult with the results
            yield FunctionResult(results)
        except Exception:
            yield FunctionError()
