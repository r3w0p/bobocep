from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    long_description = readme_file.read()

requirements = []
setup_requirements = []
test_requirements = []

setup(
    author="r3w0p",
    author_email='',
    name='bobocep',
    version='0.34.0',
    description="A fault-tolerant complex event processing engine designed "
                "for edge computing in IoT systems.",
    long_description=long_description,
    long_description_content_type='text/x-rst',
    license="MIT",
    keywords='bobocep',
    url='https://github.com/r3w0p/bobocep',

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.7',
    ],

    install_requires=requirements,
    setup_requires=setup_requirements,
    tests_require=test_requirements,
    packages=find_packages(include=['bobocep', 'bobocep.*']),
    test_suite='tests',
    zip_safe=False,
)
