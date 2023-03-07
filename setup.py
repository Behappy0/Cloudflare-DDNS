from setuptools import setup


with open("README.md", "r", encoding='utf-8') as f:
    long_description = f.read()


setup(
    name="cloudflare-ddns",
    version="1.0.0",
    license='MIT',
    description="A DDNS service for Cloudflare domain name",
    url='https://github.com/Behappy0/Cloudflare-DDNS',
    packages=['cloudflare_ddns'],
    package_data={
        'cloudflare_ddns': ['README.md', 'LICENSE']
    },
    install_requires=[],
    entry_points="""
    [console_scripts]
    cloudflare-ddns = cloudflare_ddns.cloudflare_ddns:main
    """,
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Internet :: Name Service (DNS)'
    ],
    long_description=long_description,
    long_description_content_type="text/markdown"
)
