from setuptools import setup

# python setup.py sdist bdist_wheel
# twine upload dist/*

long_description = ""

setup(
    name="tornadoweb",
    version="0.0.19",
    author="9wfox",
    author_email="568628130@qq.com",
    description="tornado web",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/9wfox/tornadoweb",
    package_data={'':['*.*']},
    packages=["tornadoweb"],
    install_requires=["tornado"],
    classifiers=[
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points='''
	[console_scripts]
	tornadoweb_init=tornadoweb.tornadoweb_init:go
    ''',
)
