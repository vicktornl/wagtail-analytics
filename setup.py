from setuptools import find_packages, setup

install_requires = ["django>=3", "wagtail>=2", "google-auth"]

test_require = [
    "black",
    "factory_boy",
    "flake8",
    "isort",
    "pytest",
    "pytest-django",
]

docs_require = []

setup(
    name="wagtail-analytics",
    version="0.3.2",
    description="",
    author="Moori",
    install_requires=install_requires,
    extras_require={"test": test_require},
    package_dir={"": "src"},
    packages=find_packages("src"),
    include_package_data=True,
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "Operating System :: Unix",
        "Programming Language :: Python :: 3",
    ],
)
