from setuptools import setup, find_packages

setup(
    name="dts-util",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "grpcio>=1.54.2",
        "grpcio-reflection>=1.54.2",
        "grpcio-tools>=1.54.2",
        "protobuf>=4.23.1",
    ],
    entry_points={
        "console_scripts": [
            "dts-util=dts_util.installer.server_installer:main",
        ],
    },
    python_requires=">=3.7",
)