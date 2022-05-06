
import click

from ..config import AWSTomlConfig
from ..utils.creds import get_creds_via_saml_request


def _process_credentials_file(role, profile_name, aws_creds, region, ttl):
    with AWSTomlConfig(profile_name) as atc:
        atc.set(profile_name, "aws_access_key_id", str(aws_creds.access_key))
        atc.set(profile_name, "aws_secret_access_key", str(aws_creds.secret_key))
        atc.set(profile_name, "aws_session_token", str(aws_creds.session))
        atc.set(profile_name, "region", region)
        atc.set(profile_name, "samiam_role", role)
        atc.set(profile_name, "ttl", ttl)


def _get_account_number(inp):
    return inp.split("(")[1].split(")")[0]


def _get_act_from_arn(inp):
    return inp.split(":")[4]


def _process_roles(roles, roles_acct_dict, saml_signoff, debug, echo_env, region, ttl):
    if roles_acct_dict is None or len(roles_acct_dict.keys()) == 0:
        raise Exception("No roles acc dict")
    if len(roles) > 0:
        click.secho('PICK NUMBER FOR ROLES: ', fg='green')
        for idx, role in enumerate(roles):
            role_str = "\t [{}]: ({}) {}".format(idx, roles_acct_dict[role], role)
            click.secho(role_str, fg='red')

    role_idx = click.prompt("Pick a role number", confirmation_prompt=True, type=int)
    role = roles[role_idx]

    return role, get_creds_via_saml_request(role, saml_signoff, debug, echo_env, region, ttl)


def _process_roles_no_acct_info(roles, saml_signoff, debug, echo_env, region, ttl):
    if len(roles) > 0:
        click.secho('PICK NUMBER FOR ROLES: ', fg='green')
        for idx, role in enumerate(roles):
            role_str = "\t [{}]: {}".format(idx, role)
            click.secho(role_str, fg='red')

    role_idx = click.prompt("Pick a role number", confirmation_prompt=True, type=int)
    role = roles[role_idx]

    return role, get_creds_via_saml_request(role, saml_signoff, debug, echo_env, region, ttl)
