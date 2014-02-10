from setuptools import setup, find_packages

setup(
    name='zeit.calendar',
    version='1.6.9.dev0',
    author='gocept',
    author_email='mail@gocept.com',
    url='https://svn.gocept.com/repos/gocept-int/zeit.cms/zeit.calendar',
    description="""\
""",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='gocept proprietary',
    namespace_packages=['zeit'],
    install_requires=[
        'setuptools',
        'z3c.etestbrowser',
        'zeit.cms>=2.14.0.dev0',
    ],
    entry_points={
        'fanstatic.libraries': [
            'zeit_calendar=zeit.calendar.browser.resources:lib',
        ],
    }
)
