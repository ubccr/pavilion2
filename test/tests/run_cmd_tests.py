from pavilion import plugins
from pavilion import commands
from pavilion.unittest import PavTestCase


class PavTestTests(PavTestCase):

    def setUp(self):
        plugins.initialize_plugins(self.pav_cfg)

    def tearDown(self):
        plugins._reset_plugins()

    def test_get_tests(self):
        """Make sure we can go through the whole process of getting tests.
            For the most part we're relying on tests of the various components
            of test_config.setup and the test_obj tests."""

        run_cmd = commands.get_command('run')

        tests = run_cmd._get_tests(self.pav_cfg,
                                   'this',
                                   [],
                                   ['hello_world'],
                                   [],
                                   {})

        # Make sure all the tests are there, under the right schedulers.
        self.assertEqual(tests['slurm'][0].name, 'hello')
        self.assertEqual(tests['raw'][0].name, 'world')
        self.assertEqual(tests['dummy'][0].name, 'narf')

        tests_file = self.TEST_DATA_ROOT



    def test_run(self):
        pass




