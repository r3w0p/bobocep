from setuptools import setup, find_packages

with open("README.md") as f:
    long_description = f.read()

with open("requirements.txt") as f:
    install_requires = f.read().splitlines()

setup(
    author="r3w0p",
    name="BoboCEP",
    version="0.9.0",
    description="A complex event processing engine designed for "
                "fault-tolerant edge computing in IoT systems.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    keywords="bobocep",
    url="https://github.com/r3w0p/bobocep",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: System :: Monitoring'
    ],
    install_requires=install_requires,
    packages=find_packages(include=['src', 'src.*']),
    test_suite='tests',
    zip_safe=False,
)
