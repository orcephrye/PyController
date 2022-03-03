from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='PyController',
    version='0.9',
    packages=['PyController'],
    include_package_data=True,
    scripts=['pyc'],
    url='https://github.com/orcephrye/PyController',
    project_urls={
        "Bug Tracker": "https://github.com/orcephrye/PyController/issues",
    },
    license='GPL-3.0',
    author='OrcephRye',
    author_email='orcephrye@gmail.com',
    description='A Game Pad/Controller key mapping utility',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: GNU GENERAL PUBLIC LICENSE v3",
        "Operating System :: Linux",
        "Topic :: Games/Entertainment"
    ],
    python_requires=">=3.7",
    install_requires=[
        'evdev',
        'psutil',
        'PyYAML',
        'PyGObject'
    ]
)
