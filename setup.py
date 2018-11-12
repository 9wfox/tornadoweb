from setuptools import setup

# python setup.py sdist bdist_wheel
# twine upload dist/*

long_description = ""

setup(
    name="tornadoweb",
    version="0.0.6",
    author="9wfox",
    author_email="568628130@qq.com",
    description="tornado web",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/9wfox/tornadoweb",
    packages=["tornadoweb"],
    classifiers=[
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
