from setuptools import setup, find_packages

setup(
    name='primevault_api_sdk',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'boto3==1.33.13',
        'cryptography==42.0.4',
    ],
    author='PrimeVault',
    description='Python SDK for PrimeVault APIs',
    url='https://github.com/horcrux01/primevault_api_sdk',
    python_requires='>=3.10.4',
)
