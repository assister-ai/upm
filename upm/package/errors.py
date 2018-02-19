class PackageSpecificationError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class PackageSpecificationAlreadyExist(PackageSpecificationError):
    def __init__(self, override_filenames):
        self.override_filenames = override_filenames
        super(PackageSpecificationAlreadyExist, self).__init__(
            "Package already exists".format(override_filenames)
        )


class PackageSpecificationNotFound(PackageSpecificationError):
    def __init__(self, supported_filenames):
        super(PackageSpecificationNotFound, self).__init__("""
        Can't find a suitable configuration file in this directory or any
        parent. Are you in the right directory?

        Supported filenames: %s
        """ % ", ".join(supported_filenames))
