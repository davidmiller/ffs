"""
Fab commands for ffs
"""

from fabric.api import task, hosts, local, lcd,  cd, run
from fabric import operations

deadpan = 'happenup@deadpansincerity.com'

@task
def test():
    """
    Run our unittests
    """
    local('python -m pytest test')

@task
def make_docs():
    """
    Rebuild the documentation
    """
    with lcd('doc/'):
        local('make html')

@task
@hosts(deadpan)
def upload_docs():
    """
    Build, compress, upload and extract the latest docs
    """
    with lcd('doc/build/html'):
        local('rm -rf ffsdocs.tar.gz')
        local('tar zcvf ffsdocs.tar.gz *')
        operations.put('ffsdocs.tar.gz', '/home/happenup/webapps/ffsdocs/ffsdocs.tar.gz')
    with cd('/home/happenup/webapps/ffsdocs/'):
        run('tar zxvf ffsdocs.tar.gz')
