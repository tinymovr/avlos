from avlos.unit_field import get_registry

try:
    from avlos._version import __version__
except ImportError:
    # Package is not installed, version will be determined from git
    try:
        from setuptools_scm import get_version
        __version__ = get_version(root='..', relative_to=__file__)
    except (ImportError, LookupError):
        __version__ = "unknown"

__all__ = ["get_registry", "__version__"]