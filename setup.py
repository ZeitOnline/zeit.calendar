from setuptools import setup, find_packages


setup(
    name='zeit.calendar',
    version='1.6.11.dev0',
    author='gocept, Zeit Online',
    author_email='zon-backend@zeit.de',
    url='http://www.zeit.de/',
    description="vivi calendar",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='BSD',
    namespace_packages=['zeit'],
    install_requires=[
        'setuptools',
        'pyramid_dogpile_cache2',
        'z3c.etestbrowser',
        'zeit.cms>=2.64.0.dev0',
    ],
    entry_points={
        'fanstatic.libraries': [
            'zeit_calendar=zeit.calendar.browser.resources:lib',
        ],
    }
)
