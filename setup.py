from setuptools import find_packages, setup

setup(
    name="primevault_api_sdk",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "boto3==1.34.84",
        "cryptography==43.0.1",
        "requests==2.32.0",
        "pytest==8.3.4",
        "dacite==1.9.1",
    ],
    author="PrimeVault",
    description="Python SDK for PrimeVault APIs",
    url="https://github.com/horcrux01/primevault_api_sdk",
    python_requires=">=3.10.4",
)
