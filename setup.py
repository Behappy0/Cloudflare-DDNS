import os
import re
import codecs
from setuptools import setup


with open("README.md", "r", encoding='utf-8') as f:
    long_description = f.read()


def read_file(filename, encoding="utf8"):
    with codecs.open(filename, encoding=encoding) as fd:
        return fd.read()


package_name = "cloudflare_ddns"
here = os.path.abspath(os.path.dirname(__file__))
init_fn = os.path.join(here, package_name, "__init__.py")
meta = dict(re.findall(r"""__([a-z]+)__ = "([^"]+)""", read_file(init_fn)))


setup(
    name="cloudflare-ddns",
    version=meta["version"],
    license='MIT',
    description="A DDNS service for Cloudflare domain name",
    author='Behappy0',
    url='https://github.com/Behappy0/Cloudflare-DDNS',
    packages=[package_name],
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
