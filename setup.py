from setuptools import setup, find_packages

with open('README.md') as f:
    long_description = f.read()

with open('requirements.txt') as f:
    install_requires = f.read().splitlines()

setup(
    author="r3w0p",
    name='BoboCEP',
    version='0.35.0',
    description="A fault-tolerant complex event processing engine designed "
                "for edge computing in IoT systems.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    license="GPL-3.0-only",
    keywords='bobocep',
    url='https://github.com/r3w0p/bobocep',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.8',
    ],
    install_requires=install_requires,
    packages=find_packages(include=['bobocep', 'bobocep.*']),
    test_suite='tests',
    zip_safe=False,
)
