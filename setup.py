from setuptools import setup, find_packages

setup(
    name="cga-lib",
    version="0.1.0",
    author="Weston Forbes",
    description="This is a package of tools used by myself, Weston Forbes, for the CG Automation Toolkit.",
    packages=find_packages(),
    python_requires=">=3.6",
    install_requires=[
        "ping3==5.1.5",
        "pylogix==1.1.4",
    ],
    classifiers=[
        "Programming Language :: Python :: 3"
    ],
) 