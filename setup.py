from setuptools import setup


setup(
    name="Cloudflare-DDNS",
    version="1.0.0",
    description="A DDNS service based on Cloudflare domain name",
    url='https://github.com/Behappy0/Cloudflare-DDNS',
    packages=['Cloudflare-DDNS'],
    package_data={
        'Cloudflare-DDNS': ['README.rst', 'LICENSE']
    },
    install_requires=[],
    entry_points="""
    [console_scripts]
    cloudflare-ddns = CloudflareDDNS:main
    """,
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Internet :: DDNS Service'
    ]
)
