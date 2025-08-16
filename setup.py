from setuptools import setup, find_packages

setup(
    name="gsql-client",
    version="1.0.0",
    author="BB",
    description="A helper library for Google Cloud SQL interactions (PostgreSQL)",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.12.0",
    install_requires=[
        "google-cloud-storage>=1.18.4",
        "SQLAlchemy>=2.0.43"
    ],
)