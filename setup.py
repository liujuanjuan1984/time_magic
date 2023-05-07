import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="time_magic",
    version="0.3.1",
    author="liujuanjuan1984",
    author_email="qiaoanlu@163.com",
    description="python tools all about time",
    keywords=["python", "timebill", "time_magic"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/liujuanjuan1984/time_magic",
    project_urls={
        "Github Repo": "https://github.com/liujuanjuan1984/time_magic",
        "Bug Tracker": "https://github.com/liujuanjuan1984/time_magic/issues",
        "About Quorum": "https://github.com/rumsystem/quorum",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(exclude=["example"]),
    python_requires=">=3.7",
    install_requires=[
        "pandas",
        "matplotlib",
    ],
)
