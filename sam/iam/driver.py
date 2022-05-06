import copy
import time

from urllib.parse import unquote


def get_saml_response(driver, debug=False, sleeptime=0.5):
    # Grok for parsing xml should redo with bsoup4
    while True:
        time.sleep(sleeptime)
        for entry in driver.get_log('performance'):
            if 'samlresponse' in str(entry).lower() and '"documenturl":"https://signin.aws.amazon.com/saml"' in str(
                    entry).lower():
                if debug == True:
                    print("Saml matches: " + str(entry))
                from pygrok import Grok
                pattern = '%{GREEDYDATA}SAMLResponse=%{DATA:samlresponse}&%{GREEDYDATA}"%{GREEDYDATA}'
                grok = Grok(pattern)
                saml_resp_enc = grok.match(str(entry))['samlresponse']
                saml_resp_dec = unquote(saml_resp_enc)
                return saml_resp_dec


def get_roles_from_saml(saml):
    # Hack for parsing xml should redo with bsoup4
    import base64

    iam_part_arn = 'arn:aws:iam::'
    saml_part_arn = ':saml-provider/'

    decodedstr = base64.b64decode(saml).decode("utf-8")
    role_arns = []
    for line in decodedstr.split("\n"):
        if iam_part_arn in line:
            parts = line.split(iam_part_arn)
            for part in parts[1:]:
                if saml_part_arn not in part:
                    rest_arn = part.split("<")[0].replace(",", "")
                    role_arns.append(iam_part_arn + rest_arn)

    return list(set(role_arns))


def get_saml_and_roles_pg_src_via_perf_logs(sso_url, debug):
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
    import os
    caps = copy.deepcopy(DesiredCapabilities.CHROME)
    sam_iam_dir = os.path.expanduser("~/.samiam/")
    chrome_data_dir_path = os.path.join(sam_iam_dir, 'chromedata')
    caps['loggingPrefs'] = {'performance': 'ALL'}
    chromedriver_options = Options()
    chromedriver_options.set_capability("loggingPrefs", {'performance': 'ALL'})
    chromedriver_options.add_argument("--log-level=ALL")  # suppress selenium logging to stdout
    chromedriver_options.add_argument("user-data-dir={}".format(chrome_data_dir_path))
    chromedriver_options.add_argument('--disable-gpu')
    chromedriver_options.add_experimental_option('w3c', False)
    try:
        driver = webdriver.Chrome(chrome_options=chromedriver_options, desired_capabilities=caps)
    except:
        import os
        driver = webdriver.Chrome(os.getenv("CHROME_DRIVER_LOC"), chrome_options=chromedriver_options,
                                  desired_capabilities=caps)

    driver.get(sso_url)

    saml = get_saml_response(driver, debug)
    if debug == True:
        print("SAML: " + saml)
    roles = get_roles_from_saml(saml)
    if debug == True:
        print("Roles: " + str(roles))
    return roles, saml, driver
