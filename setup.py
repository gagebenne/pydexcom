from setuptools import setup

with open("README.md", "r") as file:
    long_description = file.read()

setup(
    name="pydexcom",
    version="0.1.6",
    description="Python API to interact with Dexcom Share API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gagebenne/pydexcom",
    author="Gage Benne",
    author_email="gagedbenne@gmail.com",
    license="MIT",
    install_requires=["requests>=2.0"],
    packages=["pydexcom"],
    zip_safe=True,
    python_requires=">=3.6",
)
