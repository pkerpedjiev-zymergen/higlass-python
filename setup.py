from setuptools import setup, find_packages, Command
from setuptools.command.build_py import build_py
from setuptools.command.egg_info import egg_info
from setuptools.command.sdist import sdist
from subprocess import check_call
import platform
import sys
import os
import io

here = os.path.dirname(os.path.abspath(__file__))
is_repo = os.path.exists(os.path.join(here, '.git'))

STATIC_DIR = os.path.join(here, 'higlass', 'static')
NODE_ROOT = os.path.join(here, 'js')
NPM_PATH = os.pathsep.join([
    os.path.join(NODE_ROOT, 'node_modules', '.bin'),
                os.environ.get('PATH', os.defpath),
])

from distutils import log
log.set_verbosity(log.DEBUG)
log.info('setup.py entered')
log.info('$PATH=%s' % os.environ['PATH'])


def read(*parts, **kwargs):
    filepath = os.path.join(here, *parts)
    encoding = kwargs.pop('encoding', 'utf-8')
    with io.open(filepath, encoding=encoding) as fh:
        text = fh.read()
    return text


def get_version(*parts):
    version_ns = {}
    with open(os.path.join(here, *parts)) as f:
        exec(f.read(), {}, version_ns)
    return version_ns['__version__']


def js_prerelease(command, strict=False):
    """decorator for building minified js/css prior to another command"""
    class DecoratedCommand(command):
        def run(self):
            jsdeps = self.distribution.get_command_obj('jsdeps')
            if not is_repo and all(os.path.exists(t) for t in jsdeps.targets):
                # sdist, nothing to do
                command.run(self)
                return

            try:
                self.distribution.run_command('jsdeps')
            except Exception as e:
                missing = [t for t in jsdeps.targets if not os.path.exists(t)]
                if strict or missing:
                    log.warn('rebuilding js and css failed')
                    if missing:
                        log.error('missing files: %s' % missing)
                    raise e
                else:
                    log.warn('rebuilding js and css failed (not a problem)')
                    log.warn(str(e))
            command.run(self)
            update_package_data(self.distribution)
    return DecoratedCommand


def update_package_data(distribution):
    """update package_data to catch changes during setup"""
    build_py = distribution.get_command_obj('build_py')
    # distribution.package_data = find_package_data()
    # re-init build_py options which load package_data
    build_py.finalize_options()


class NPM(Command):
    description = 'install package.json dependencies using npm'

    user_options = []

    node_modules = os.path.join(NODE_ROOT, 'node_modules')

    targets = [
        os.path.join(STATIC_DIR, 'extension.js'),
        os.path.join(STATIC_DIR, 'index.js'),
    ]

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def get_npm_name(self):
        npmName = 'npm';
        if platform.system() == 'Windows':
            npmName = 'npm.cmd'
        return npmName

    def has_npm(self):
        npmName = self.get_npm_name();
        try:
            check_call([npmName, '--version'])
            return True
        except:
            return False

    def should_run_npm_install(self):
        package_json = os.path.join(NODE_ROOT, 'package.json')
        node_modules_exists = os.path.exists(self.node_modules)
        return self.has_npm() and not node_modules_exists

    def run(self):
        has_npm = self.has_npm()
        if not has_npm:
            log.error(
                "`npm` unavailable.  If you're running this command using "
                "sudo, make sure `npm` is available to sudo")

        env = os.environ.copy()
        env['PATH'] = NPM_PATH

        npmName = self.get_npm_name();

        if self.should_run_npm_install():
            log.info(
                "Installing build dependencies with npm.  "
                "This may take a while...")
            check_call(
                [npmName, 'install'],
                cwd=NODE_ROOT, stdout=sys.stdout, stderr=sys.stderr)
            os.utime(self.node_modules, None)

        check_call(
            [npmName, 'run', 'build'],
            cwd=NODE_ROOT, stdout=sys.stdout, stderr=sys.stderr)

        for t in self.targets:
            if not os.path.exists(t):
                msg = 'Missing file: %s' % t
                if not has_npm:
                    msg += '\nnpm is required to build a development version '
                    'of a widget extension'
                raise ValueError(msg)

        # update package data in case this created new files
        update_package_data(self.distribution)


setup_args = {
    'name': 'higlass-python',
    'version': get_version('higlass', '_version.py'),
    'packages': find_packages(),
    'license': 'MIT',
    'description': 'Python bindings for the HiGlass viewer',
    'long_description': read('README.md'),
    'long_description_content_type': 'text/markdown',
    'url': 'https://github.com/higlass/higlass-python',
    'include_package_data': True,
    'zip_safe': False,
    'author': 'Peter Kerpedjiev',
    'author_email': 'pkerpedjiev@gmail.com',
    'keywords': [
        'higlass',
    ],
    'classifiers': [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Multimedia :: Graphics',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    'install_requires': [
        'clodius',
        'flask',
    ],
    'setup_requires': [
    ],
    'tests_require': [
        'pytest'
    ],
    'cmdclass': {
        'build_py': js_prerelease(build_py),
        'egg_info': js_prerelease(egg_info),
        'sdist': js_prerelease(sdist, strict=True),
        'jsdeps': NPM,
    },
}

setup(**setup_args)
