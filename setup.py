from setuptools import setup, find_packages

with open("README.md") as f:
    long_description = f.read()

with open("requirements.txt") as f:
    install_requires = f.read().splitlines()

setup(
    name="bobocep",
    version="1.2.0",
    author="r3w0p",
    author_email="rr33ww00pp@gmail.com",
    description="A fault-tolerant Complex Event Processing engine "
                "designed for edge computing in Internet of Things systems.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/r3w0p/bobocep",
    keywords=[
        "complex event processing",
        "distributed systems",
        "edge computing",
        "fault tolerance",
        "internet of things",
        "web of things"
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Distributed Computing",
        "Topic :: System :: Monitoring"
    ],
    install_requires=install_requires,
    packages=find_packages(include=["bobocep", "bobocep.*"]),
    test_suite="tests",
    zip_safe=False
)
