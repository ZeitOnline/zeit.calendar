import pkg_resources
import pyramid_dogpile_cache2
import zeit.calendar.testing
import zope.app.appsetup.product
import zope.component


class RessortGroupManagerTest(zeit.calendar.testing.FunctionalTestCase):

    def setUp(self):
        super(RessortGroupManagerTest, self).setUp()
        self.manager = zope.component.getUtility(
            zeit.calendar.interfaces.IRessortGroupManager)

    def tearDown(self):
        self._set_rules('ressortgroups.xml')
        super(RessortGroupManagerTest, self).tearDown()

    def _set_rules(self, filename):
        config = zope.app.appsetup.product._configs['zeit.calendar']
        config['ressortgroup-url'] = (
            'file://' + pkg_resources.resource_filename(
                'zeit.calendar.tests.fixtures', filename))
        pyramid_dogpile_cache2.clear()

    def test_valid_file_should_be_loaded(self):
        self._set_rules('ressortgroups.xml')
        self.assertEqual(4, len(self.manager.groups))
        self.assertEqual('Politik', self.manager.groups[0]['title'])
        self.assertEqual('politik', self.manager.css('International'))
        self.assertEqual('misc', self.manager.css('Unbekannt'))

    def test_syntax_error_should_keep_previous_values(self):
        self._set_rules('ressortgroups.xml')
        self.assertEqual(4, len(self.manager.groups))
        self._set_rules('syntaxerror.xml')
        self.assertEqual(4, len(self.manager.groups))
