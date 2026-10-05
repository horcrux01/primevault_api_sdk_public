from setuptools import find_packages, setup

from primevault_python_sdk.version import __version__

setup(
    name="primevault_api_sdk",
    version=__version__,
    packages=find_packages(),
    install_requires=[
        "boto3==1.34.84",
        "cryptography==50.0.0",
        "requests==2.33.0",
        "pytest==9.0.3",
        "dacite==1.9.1",
    ],
    author="PrimeVault",
    description="Python SDK for PrimeVault APIs",
    url="https://github.com/horcrux01/primevault_api_sdk",
    python_requires=">=3.9",
)
