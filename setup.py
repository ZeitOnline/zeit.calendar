from setuptools import setup, find_packages

setup(
    name='zeit.calendar',
    version='1.3dev',
    author='gocept',
    author_email='mail@gocept.com',
    url='https://svn.gocept.com/repos/gocept-int/zeit.cms/zeit.calendar',
    description="""\
""",
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data = True,
    zip_safe=False,
    license='gocept proprietary',
    namespace_packages = ['zeit'],
    install_requires=[
        'setuptools',
        'zeit.cms>=1.1.3',
    ],
    extras_require={
        'test': [
            'z3c.etestbrowser',
        ],
    },
)
