from setuptools import setup


setup(
    name="Cloudflare-DDNS",
    version="1.0.0",
    description="A DDNS service based on Cloudflare domain name",
    url='https://github.com/shadowsocks/shadowsocks',
    install_requires=[],
    entry_points="""
    [console_scripts]
    cloudflare-ddns = CloudflareDDNS:main
    """
)
