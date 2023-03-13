from setuptools import setup
from cloudflare_ddns import __version__ as package_version


with open("README.md", "r", encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="cloudflare-ddns",
    version=package_version,
    license='MIT',
    description="A DDNS service for Cloudflare domain name",
    author='Behappy0',
    url='https://github.com/Behappy0/Cloudflare-DDNS',
    packages=['cloudflare_ddns'],
    include_package_data=True,
    install_requires=[],
    python_requires=">=3.9",
    entry_points="""
    [console_scripts]
    cloudflare-ddns = cloudflare_ddns.service:main
    """,
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Internet :: Name Service (DNS)'
    ],
    long_description=long_description,
    long_description_content_type="text/markdown"
)
