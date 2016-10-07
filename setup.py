from setuptools import setup, find_packages


VERSION = open('VERSION').read()


setup(
    name='psu.oit.rt',
    version=VERSION,
    description='RT REST API Wrapper',
    keywords='Request Tracker, RT, REST',
    license='MIT',
    author='PSU - OIT - WDT',
    author_email='webteam@pdx.edu',
    maintainer='Wyatt Baldwin',
    maintainer_email='wbaldwin@pdx.edu',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'requests>=2.11.1',
    ],
    extras_require={
        'dev': [
            'coverage',
            'flake8',
        ]
    },
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
