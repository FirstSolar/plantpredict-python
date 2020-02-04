import os
from setuptools import setup

__currdir__ = os.getcwd()
__readme__ = os.path.join(__currdir__, 'README.md')

setup(
    name='plantpredict',
    version='0.9.4',
    description='Python SDK for PlantPredict (https://ui.plantpredict.com).',
    url='https://github.com/stephenkaplan/plantpredict-python',
    author='Stephen Kaplan, Performance & Prediction Engineer at First Solar, Inc.',
    author_email='stephen.kaplan@firstsolar.com',
    license='LICENSE.txt',
    long_description=open(__readme__).read(),
    packages=['plantpredict'],
    python_requires='>=3.5, <4',
    install_requires=[
        'requests',
        'pandas',
        'six',
        'mock',
        'xlrd',
        'openpyxl'
    ]
)
