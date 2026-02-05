from setuptools import setup, find_packages

setup(
    name="growpodempire",
    version="1.0.0",
    description="Professional cannabis cultivation management platform",
    author="GrowPodEmpire Team",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "flask>=3.0.0",
        "flask-cors>=4.0.0",
        "sqlalchemy>=2.0.23",
        "pydantic>=2.5.0",
        "python-dotenv>=1.0.0",
        "numpy>=1.26.2",
        "pandas>=2.1.4",
    ],
)
