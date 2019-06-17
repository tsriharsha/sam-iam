

class AWSCreds:

    def __init__(self, access_key, secret_key, session) -> None:
        super().__init__()
        self.session = session
        self.secret_key = secret_key
        self.access_key = access_key


def __get_act_from_arn(inp):
    return inp.split(":")[4]


def __click_output(debug, echo_env, response):
    import click
    if debug is True:
        click.secho('\n' * 10)
        click.secho("=" * 30)
        click.secho("#AWS CONFIG CREDENTIALS FILE")
        click.secho("=" * 30)
        click.secho('[tempaccount]')
        click.secho('aws_access_key_id = {}'.format(response['Credentials']['AccessKeyId']))
        click.secho('aws_secret_access_key = {}'.format(response['Credentials']['SecretAccessKey']))
        click.secho('aws_session_token = {}'.format(response['Credentials']['SessionToken']))
        click.secho('region = us-east-1')
        click.secho()
        click.secho("=" * 30)
        click.secho("#AWS ENV VARIABLES")
        click.secho("=" * 30)
        click.secho('export AWS_ACCESS_KEY_ID={}'.format(response['Credentials']['AccessKeyId']))
        click.secho('export AWS_SECRET_ACCESS_KEY={}'.format(response['Credentials']['SecretAccessKey']))
        click.secho('export AWS_SESSION_TOKEN={}'.format(response['Credentials']['SessionToken']))
        click.secho('export AWS_DEFAULT_REGION=us-east-1')
    if echo_env is True:
        click.secho('=' * 100, fg='blue')
        click.secho('export AWS_ACCESS_KEY_ID={}'.format(response['Credentials']['AccessKeyId']))
        click.secho('export AWS_SECRET_ACCESS_KEY={}'.format(response['Credentials']['SecretAccessKey']))
        click.secho('export AWS_SESSION_TOKEN={}'.format(response['Credentials']['SessionToken']))
        click.secho('export AWS_DEFAULT_REGION=us-east-1')
        click.secho('=' * 100, fg='blue')


def __console_output(debug, echo_env, response):
    if debug is True:
        print('\n' * 10)
        print("=" * 30)
        print("#AWS CONFIG CREDENTIALS FILE")
        print("=" * 30)
        print('[tempaccount]')
        print('aws_access_key_id = {}'.format(response['Credentials']['AccessKeyId']))
        print('aws_secret_access_key = {}'.format(response['Credentials']['SecretAccessKey']))
        print('aws_session_token = {}'.format(response['Credentials']['SessionToken']))
        print('region = us-east-1')
        print()
        print("=" * 30)
        print("#AWS ENV VARIABLES")
        print("=" * 30)
        print('export AWS_ACCESS_KEY_ID={}'.format(response['Credentials']['AccessKeyId']))
        print('export AWS_SECRET_ACCESS_KEY={}'.format(response['Credentials']['SecretAccessKey']))
        print('export AWS_SESSION_TOKEN={}'.format(response['Credentials']['SessionToken']))
        print('export AWS_DEFAULT_REGION=us-east-1')
    if echo_env is True:
        print('=' * 100)
        print('export AWS_ACCESS_KEY_ID={}'.format(response['Credentials']['AccessKeyId']))
        print('export AWS_SECRET_ACCESS_KEY={}'.format(response['Credentials']['SecretAccessKey']))
        print('export AWS_SESSION_TOKEN={}'.format(response['Credentials']['SessionToken']))
        print('export AWS_DEFAULT_REGION=us-east-1')
        print('=' * 100)


def __get_provider(arn1, arn2):
    if 'saml-provider' in arn1:
        return arn1
    return arn2


def __get_role(arn1, arn2):
    if 'role' in arn1:
        return arn1
    return arn2


def __get_saml_roles_providers_from_saml(saml):
    import base64

    iam_part_arn = 'arn:aws:iam::'

    decodedstr = base64.b64decode(saml).decode("utf-8")
    arns = []
    for line in decodedstr.split("\n"):
        if iam_part_arn in line:
            parts = line.split(iam_part_arn)
            for part in parts[1:]:
                # if saml_part_arn not in part:
                arn = part.split("<")[0].replace(",", "")
                arns.append(iam_part_arn + arn)
    role_provider_dict = {}
    it = iter(arns)
    for x in it:
        arn1 = x
        arn2 = next(it)
        role_provider_dict[__get_role(arn1, arn2)] = __get_provider(arn1, arn2)
    return role_provider_dict


def get_creds_via_saml_request(role, saml, debug, echo_env, cli=True):
    import boto3
    client = boto3.client("sts")
    role_provider_dict = __get_saml_roles_providers_from_saml(saml)
    principal_arn = role_provider_dict[role]
    response = client.assume_role_with_saml(
            RoleArn=role,
            PrincipalArn=principal_arn,
            SAMLAssertion=saml
    )

    if cli is True:
        __click_output(debug, echo_env, response)
    else:
        __console_output(debug, echo_env, response)

    return AWSCreds(response['Credentials']['AccessKeyId'],
                    response['Credentials']['SecretAccessKey'],
                    response['Credentials']['SessionToken'])
