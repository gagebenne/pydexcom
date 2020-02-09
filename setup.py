from setuptools import setup

setup(
    name='pydexcom',
    version='0.0.1',
    description='Python API to interact with Dexcom Share API',
    url='https://github.com/gagebenne/pydexcom',
    author='Gage Benne',
    author_email='gagedbenne@gmail.com',
    license='MIT',
    install_requires=['requests>=2.0'],
    packages=['pydexcom'],
    zip_safe=True
)
