# -*- coding: utf-8 -*-
# pragma pylint: disable=unused-argument, no-self-use
"""Function implementation"""

import logging
from resilient_circuits import ResilientComponent, function, handler, StatusMessage, FunctionResult, FunctionError
from fn_aws.util.helper import AWSHelper
import json

PACKAGE_NAME = "fn_aws"


class FunctionComponent(ResilientComponent):
    """Component that implements Resilient function 'aws_lambda_invoke_function''"""

    def __init__(self, opts):
        """constructor provides access to the configuration options"""
        super(FunctionComponent, self).__init__(opts)
        self.options = opts.get(PACKAGE_NAME, {})

    @handler("reload")
    def _reload(self, event, opts):
        """Configuration options have changed, save new values"""
        self.options = opts.get(PACKAGE_NAME, {})

    @function("aws_lambda_invoke_function")
    def _aws_lambda_invoke_function_function(self, event, *args, **kwargs):
        """Function: None"""
        try:

            # Get the wf_instance_id of the workflow this Function was called in
            wf_instance_id = event.message["workflow_instance"]["workflow_instance_id"]

            yield StatusMessage("Starting 'aws_lambda_invoke_function' running in workflow '{0}'".format(wf_instance_id))

            # Get the function parameters:
            aws_lambda_payload = kwargs.get("aws_lambda_payload")  # text
            aws_lambda_function_name = kwargs.get("aws_lambda_function_name")  # text
            aws_region = kwargs.get("aws_region")  # text
            aws_access_key_name = kwargs.get("aws_access_key_name")  # text

            log = logging.getLogger(__name__)
            log.info("aws_lambda_payload: %s", aws_lambda_payload)
            log.info("aws_lambda_function_name: %s", aws_lambda_function_name)
            log.info("aws_region: %s", aws_region)
            log.info("aws_access_key_name: %s", aws_access_key_name)
            yield StatusMessage("Function Inputs OK")


            # Instansiate helper (which gets appconfigs from file)
            helper = AWSHelper(self.options, aws_access_key_name)    
            yield StatusMessage("Appconfig Settings OK")

            # Create Lambda client
            lambda_client = helper.get_client('lambda', aws_region)
            yield StatusMessage("Lambda Client created")


            ##############################################
            success = False
            res_json = {}

            # Validate aws_tag_names format and convert to bytes
            if aws_lambda_payload is None or aws_lambda_payload == '':
                event = {}
            else:
                try:
                    event = json.dumps(json.loads(aws_lambda_payload), default=str).encode('utf-8')
                except Exception as e:
                    raise ValueError("Illegal format for aws_lambda_payload.\n Error: {0}".format(e))

            try:
                res = lambda_client.invoke(FunctionName=aws_lambda_function_name, LogType='Tail', Payload=event)
                if res['ResponseMetadata']['HTTPStatusCode'] == 200:

                    res_json = json.loads(json.dumps(res, default=str))
                    success = True
                else:
                    log.error('Cannot invoke lambda funtion.\n{}\n'.format(str(res)))

            except Exception as e:
                raise ValueError("Cannot invoke lambda function.\n Error: {0}".format(e))

            ##############################################

            yield StatusMessage("Finished 'aws_lambda_invoke_function' that was running in workflow '{0}'".format(wf_instance_id))

            results = {
                "success": success,
                "lambdaResult": res_json
            }

            # Produce a FunctionResult with the results
            yield FunctionResult(results)
        except Exception:
            yield FunctionError()
