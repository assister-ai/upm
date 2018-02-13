import click
from package.errors import PackageSpecificationAlreadyExist
from package.specification import package_exists, PackageSpecification, dump_yaml


def initialize_package(working_dir):

    def get_user_input():
        base_types = ['default', 'image', 'file']
        name = click.prompt('Please enter project name', type=str)
        author = click.prompt('Please enter project author', type=str)
        description = click.prompt('Please enter project description', type=str)
        version = click.prompt('Please enter project version', default='0.0.1', type=str)
        base_type = click.prompt('Do you have docker file or image ? or default for thine image',
                                 default='default',
                                 type=click.Choice(base_types))

        if base_type is base_types[1]:
            image = click.prompt('Please enter DockerImage', default='alpine:3.6', type=str)
            base = {'image': image}
        elif base_type is base_types[2]:
            build = click.prompt('Please enter Dockerfile path', default='./Dockerfile', type=str)
            base = {'build': build}
        elif base_type is base_types[0]:
            image = 'alpine:3.6'
            base = {'image': image}
        else:
            raise ValueError('bad input')

        executable_flag = True
        executables = []
        while executable_flag:
            entry_name = click.prompt('Please enter executable name', default='run', type=str)
            entry_command = click.prompt('please enter command', default='npm start', type=str)
            executable_flag = click.prompt('more entrypoint?', default=False, type=bool)
            executables.append({entry_name: entry_command})

        return name, author, description, version, base, executables

    def from_prompt(package_dir):
        if package_exists(package_dir):
            raise PackageSpecificationAlreadyExist('upm.yml')
        else:
            name, author, description, version, base, executables = get_user_input()
            package = PackageSpecification(name, author, version, description, executables, base)
            dump_yaml(dict(package._asdict()), package_dir)
            print("project initialized")
            return package

    from_prompt(working_dir)
