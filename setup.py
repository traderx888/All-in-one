from setuptools import setup, find_packages

setup(
    name="all-in-one",
    version="0.1.0",
    description="Multi-Agent Trading System",
    author="traderx888",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
)
