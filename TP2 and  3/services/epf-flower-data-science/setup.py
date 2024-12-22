from setuptools import setup, find_packages

setup(
    name="epf-flower-data-science",
    version="0.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "gunicorn~=20.1",
        "uvicorn==0.17.6",
        "fastapi==0.95.1",
        "fastapi-utils==0.2.1",
        "pydantic==1.10",
        "opendatasets",
        "pytest",
        "validators",
        "httpx",
        "scikit-learn",
        "pytest-asyncio",
        "slowapi",
    ],
)
