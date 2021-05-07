import logging
import boto3
import botocore.config
import botocore.exceptions

log = logging.getLogger(__name__)

class AWSHelper:

    @staticmethod
    def __get_config_option(app_configs, option_name, optional=False, placeholder=None):
        """Given option_name, checks if it is in appconfig. Raises ValueError if a mandatory option is missing"""
        option = app_configs.get(option_name)
        err = "'{0}' is mandatory and is not set in app.config file. You must set this value to run this function".format(option_name)

        if not optional and not option:
            raise ValueError(err)
        elif not optional and option:
            return option
        elif optional and option:
            if option_name == 'sg_ec2_containment':
                return option.split(',')
            else:
                return option
        else:
            return None


    def __init__(self, app_configs, access_key):

        if access_key is None or access_key == '':
            # Default access key credentials
            self.AWS_ACCESS_KEY_ID = self.__get_config_option(app_configs=app_configs, option_name='aws_access_key_id', optional=False)
            self.AWS_SECRET_ACCESS_KEY = self.__get_config_option(app_configs=app_configs, option_name='aws_secret_access_key', optional=False)
            log.info('Using default access key')
        else:
            # Special credentials entered in function
            self.AWS_ACCESS_KEY_ID = self.__get_config_option(app_configs=app_configs, option_name=access_key+'_aws_access_key_id', optional=False)
            self.AWS_SECRET_ACCESS_KEY = self.__get_config_option(app_configs=app_configs, option_name=access_key+'_aws_secret_access_key', optional=False)
            log.info('Using {} access key'.format(access_key))

        self.AWS_DEFAULT_REGION = self.__get_config_option(app_configs=app_configs, option_name='default_region', optional=False)
        #self.ISOLATION_SECURITY_GROUPS = self.__get_config_option(app_configs=app_configs, option_name='sg_ec2_containment', optional=True, placeholder='sg-isolation-1,sg-isolation-2')
        self.HTTP_PROXY = {}
        if app_configs.get('http_proxy'):
            self.HTTP_PROXY['http'] = self.__get_config_option(app_configs=app_configs, option_name='http_proxy', optional=True)
        if app_configs.get('https_proxy'):
            self.HTTP_PROXY['https'] = self.__get_config_option(app_configs=app_configs, option_name='https_proxy', optional=True)



    def get_client(self, service_name, region_name):
        # Create an AWS boto3 client instance for the specified AWS service name.
        try:
            self.client = boto3.client(
                #region_name = region_name,
                region_name = (self.AWS_DEFAULT_REGION if region_name is None or region_name == '' else region_name),
                aws_access_key_id = self.AWS_ACCESS_KEY_ID,
                aws_secret_access_key = self.AWS_SECRET_ACCESS_KEY,
                service_name=service_name,
                config=botocore.config.Config(proxies=self.HTTP_PROXY))

        except botocore.exceptions.ClientError as cli_ex:
            log.error("ERROR instantiating AWS client for service: %s, Got exception : %s",
                      service_name, cli_ex.__repr__())
            raise cli_ex

        return self.client
