import click
from click import ClickException

from .. import load_logo
from .driver import get_saml_and_roles_pg_src_via_perf_logs
from .helper import _process_credentials_file, _get_account_number, _get_act_from_arn, _process_roles, \
    _process_roles_no_acct_info
from ..config import AWSTomlConfig
from ..config import load_config
from ..utils.creds import get_creds_via_saml_request


@click.group(name='iam')
def iam():
    """
        Basic Setup of the Ping 2 Aws Federated Programmatic Access Creation via a automated process.
    """
    pass


@iam.command("get-creds")
@click.option('-v', '--verbose', 'debug', is_flag=True, default=False, help='Debug messages (default=False)')
@click.option('-s', '-sso-url', 'sso_url',
              help='SSO url for idp which is ping url.')
@click.option('-p', '-profile-name', 'profile_name',
              default="temp_sso_creds",
              help='Default profile name that you want to store in credentials file. (default=temp_sso_creds')
@click.option('-d', '--use-default-profile', 'default', is_flag=True, default=False,
              help='Forcefully use default profile for aws configuration. (default=False)')
@click.option('-e', '--echo-creds', 'echo', is_flag=True, default=False,
              help='Echo creds to console. (default=False)')
@load_config
@load_logo
def get_creds(debug, sso_url, profile_name, default, echo):
    """
        Automatically retrieve aws credentials using chromedriver.

        Sample uses:

            1) samiam auto -e -p <profile_name>

            2) samiam auto --use-default-profile

            2) samiam auto
    """
    if default is True:
        profile_name = 'default'

    try:
        import os
        sso_url = os.environ.get('AWS_SSO_URL', sso_url)
        roles, saml_signoff, driver = get_saml_and_roles_pg_src_via_perf_logs(sso_url, debug)

        roles_acct_dict = None
        cred_failure = False
        try:
            # saml_signoff = driver.find_element_by_name('SAMLResponse').get_attribute('value')
            if debug is True:
                click.secho(str(driver.page_source))

            saml_accounts_dict = {_get_account_number(saml_acc.text): saml_acc.text.replace("Account: ", '') for
                                  saml_acc
                                  in
                                  driver.find_elements_by_class_name('saml-account-name')}
            if debug is True:
                click.secho(str(saml_accounts_dict))

            _roles = [label.get_attribute('for') for label in driver.find_elements_by_tag_name("label")]

            roles_acct_dict = {role: saml_accounts_dict[_get_act_from_arn(role)] for role in _roles}


            if debug is True:
                click.secho(str(roles_acct_dict))

        except:
            cred_failure = True

    finally:
        driver.close()
        driver.quit()

    try:
        role, creds = _process_roles(_roles, roles_acct_dict, saml_signoff, debug, echo)
    except:
        cred_failure = True

    if cred_failure is True:
        role, creds = _process_roles_no_acct_info(roles, saml_signoff, debug, echo)

    _process_credentials_file(role, profile_name, creds)

    click.secho('Loaded credentials to ~/.aws/credentials', fg='green')


@iam.command('refresh')
@click.option('-v', '--verbose', 'debug', is_flag=True, default=False, help='Debug messages (default=False)')
@click.option('-s', '-sso-url', 'sso_url',
              help='SSO url for idp which is ping url.')
@click.option('-d', '--use-default-profile', 'default', is_flag=True, default=False,
              help='Forcefully use default profile for aws configuration. (default=False)')
@click.option('-e', '--echo-creds', 'echo', is_flag=True, default=False,
              help='Echo creds to console. (default=False)')
@load_config
@load_logo
def refresh(debug, sso_url, default, echo):
    """
        Refresh samiam managed profile by either automatically retrieving credentials via chromedriver.

        Sample uses:

            1) samiam refresh

    """

    if default is True:
        profile_name = 'default'
    else:
        profile_name = click.prompt("Please enter samiam managed profile to refresh role creds",
                                    default='temp_sso_creds')

    try:
        with AWSTomlConfig(profile_name) as atc:
            role_arn = atc.get(profile_name, 'samiam_role')
    except Exception as e:
        raise ClickException("Error retrieving samiam_role to refresh with error: {}".format(str(e)))

    try:
        import os
        sso_url = os.environ.get('AWS_SSO_URL', sso_url)
        _, saml_signoff, driver = get_saml_and_roles_pg_src_via_perf_logs(sso_url, debug)

    finally:
        driver.close()
        driver.quit()

    creds = get_creds_via_saml_request(role_arn, saml_signoff, debug, echo)

    _process_credentials_file(role_arn, profile_name, creds)

    click.secho('Loaded credentials to ~/.aws/credentials', fg='green')
