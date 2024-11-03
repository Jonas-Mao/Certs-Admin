# -*- coding: utf-8 -*-

"""
https://github.com/certbot/certbot/blob/master/acme/examples/http01_example.py

Example ACME-V2 API for HTTP-01 challenge.

Limitations of this example:
    - Works for only one Domain name
    - Performs only HTTP-01 challenge
    - Uses ACME-v2

Workflow:
    (Account creation)
    - Create account key
    - Register account and accept TOS
    (Certificate actions)
    - Select HTTP-01 within offered challenges by the CA server
    - Set up http challenge resource
    - Set up standalone web server
    - Create domain private key and CSR
    - Issue certificate
    - Renew certificate
    - Revoke certificate
    (Account update actions)
    - Change contact information
    - Deactivate Account
"""
import ast
import json
import os
from datetime import datetime, timedelta
import OpenSSL
import josepy as jose
import requests
from acme import challenges
from acme import client
from acme import crypto_util
from acme import errors
from acme import messages
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from certs_admin.config.runtime_config import ACME_DIR
from certs_admin.utils.acme_util.challenge_type import ChallengeType
from certs_admin.utils.acme_util import directory_type_enum
from certs_admin.utils.acme_util.directory_type_enum import DirectoryTypeEnum
from certs_admin.utils.acme_util.key_type_enum import KeyTypeEnum
from certs_admin.utils.django_ext.app_exception import AppException, NotSupportedAppException


# ACME V2 测试环境
DIRECTORY_URL = 'https://acme-staging-v02.api.letsencrypt.org/directory'

# ACME V2 生产环境
# DIRECTORY_URL = "https://acme-v02.api.letsencrypt.org/directory"

# zerossl
# https://zerossl.com/documentation/acme/
# DIRECTORY_URL = "https://acme.zerossl.com/v2/DV90/directory"

USER_AGENT = 'certs-admin'

ACC_KEY_BITS = 2048

CERT_PKEY_BITS = 2048

# account.key
def get_account_key_filename(directory_type=DirectoryTypeEnum.LETS_ENCRYPT):
    return os.path.join(ACME_DIR, directory_type + '-account.key')

# account.json
def get_account_data_filename(directory_type=DirectoryTypeEnum.LETS_ENCRYPT):
    return os.path.join(ACME_DIR, directory_type + '-account.json')


def new_csr_comp(domains, pkey_pem=None):
    """
    Create certificate signing request.
    """
    if pkey_pem is None:
        pkey = OpenSSL.crypto.PKey()
        pkey.generate_key(type=OpenSSL.crypto.TYPE_RSA, bits=CERT_PKEY_BITS)
        pkey_pem = OpenSSL.crypto.dump_privatekey(
            OpenSSL.crypto.FILETYPE_PEM, pkey)

    domains = ast.literal_eval(domains)
    csr_pem = crypto_util.make_csr(pkey_pem, domains)

    return pkey_pem, csr_pem


def select_http01_chall(orderr):
    authz_list = orderr.authorizations
    for authz in authz_list:
        for i in authz.body.challenges:
            if isinstance(i.chall, challenges.HTTP01):
                return i

    raise Exception('HTTP-01 challenge was not offered by the CA server.')


def select_challenge(orderr):
    """
    Extract authorization resource from within order resource.
    """
    challenge_map = {}

    for authz in orderr['authorizations']:
        domain_challenge = []
        domain = authz.body.identifier.value

        for challenge in authz.body.challenges:
            if isinstance(challenge.chall, challenges.DNS01):
                domain_challenge.append(challenge)
            elif isinstance(challenge.chall, challenges.HTTP01):
                domain_challenge.append(challenge)

        challenge_map[domain] = domain_challenge

    return challenge_map


def select_challenge_by(orderr, domain, challenge_type):
    domain_challenges = select_challenge(orderr)[domain]

    for challenge in domain_challenges:
        if challenge_type == ChallengeType.HTTP01 and isinstance(challenge.chall, challenges.HTTP01):
            return challenge
        elif challenge_type == ChallengeType.DNS01 and isinstance(challenge.chall, challenges.DNS01):
            return challenge
        else:
            raise AppException('not found challenge')


def perform_http01(client_acme, orderr):

    deadline = datetime.now() + timedelta(seconds=10)

    try:
        finalized_orderr = client_acme.poll_and_finalize(orderr, deadline)
    except errors.TimeoutError as e:
        raise AppException("证书获取超时")

    return finalized_orderr.fullchain_pem


def get_account_key(directory_type=DirectoryTypeEnum.LETS_ENCRYPT):
    """
    Python cryptography库及RSA非对称加密
    https://blog.csdn.net/photon222/article/details/109447327
    """
    account_key_filename = get_account_key_filename(directory_type)

    if os.path.exists(account_key_filename):

        with open(account_key_filename, "rb") as f:
            private_key = serialization.load_pem_private_key(
                f.read(),
                password=None,
                backend=default_backend()
            )
    else:
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=ACC_KEY_BITS,
            backend=default_backend())

        pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        with open(account_key_filename, 'wb') as f:
            f.write(pem)

    return private_key


def ensure_account_exists(client_acme, directory_type=DirectoryTypeEnum.LETS_ENCRYPT):
    """
    确保账户存在
    """
    account_data_filename = get_account_data_filename(directory_type)

    if os.path.exists(account_data_filename):
        # 账户已存在
        with open(account_data_filename, 'r') as f:
            account_data = json.loads(f.read())

        try:
            account_resource = messages.RegistrationResource.from_json(account_data)
            account = client_acme.query_registration(account_resource)
        except errors.Error as e:
            create_account(client_acme, directory_type)
    else:
        # 账户不存在
        create_account(client_acme, directory_type)


def get_zerossl_eab():
    """
    {
        "success": true,
        "eab_kid": "",
        "eab_hmac_key": ""
    }
    """
    url = 'https://api.zerossl.com/acme/eab-credentials-email'
    res = requests.post(
        url=url,
        data={'email': "admin@certs-admin.com"}
    )

    return res.json()


def create_account(client_acme, directory_type=DirectoryTypeEnum.LETS_ENCRYPT):
    account_data_filename = get_account_data_filename(directory_type)

    if client_acme.external_account_required():
        config = get_zerossl_eab()

        eab = messages.ExternalAccountBinding.from_data(
            account_public_key=client_acme.net.key.public_key(),
            kid=config['eab_kid'],
            hmac_key=config['eab_hmac_key'],
            directory=client_acme.directory
        )
    else:
        eab = None

    new_account = messages.NewRegistration.from_data(
        terms_of_service_agreed=True,
        external_account_binding=eab
    )

    register = client_acme.new_account(new_account)

    with open(account_data_filename, 'w') as f:
        f.write(json.dumps(register.to_json(), indent=2))


def get_acme_client(directory_type=DirectoryTypeEnum.LETS_ENCRYPT, key_type=KeyTypeEnum.RSA):

    if not directory_type:
        directory_type = DirectoryTypeEnum.LETS_ENCRYPT

    directory_url = directory_type_enum.get_directory_url(directory_type)
    if not directory_url:
        raise AppException("not found directory_url")

    private_key = get_account_key(directory_type)

    if key_type == KeyTypeEnum.EC:
        account_key = jose.JWKEC(key=private_key)
        public_key = account_key.key
        if public_key.key_size == 256:
            alg = jose.ES256
        elif public_key.key_size == 384:
            alg = jose.ES384
        elif public_key.key_size == 521:
            alg = jose.ES512
        else:
            raise NotSupportedAppException("No matching signing algorithm can be found for the key")
    else:
        alg = jose.RS256
        account_key = jose.JWKRSA(key=jose.ComparableRSAKey(private_key))

    net = client.ClientNetwork(account_key, alg=alg, user_agent=USER_AGENT)

    directory = client.ClientV2.get_directory(url=directory_url, net=net)
    client_acme = client.ClientV2(directory=directory, net=net)

    ensure_account_exists(client_acme, directory_type)

    return client_acme


if __name__ == '__main__':
    print(get_zerossl_eab())
