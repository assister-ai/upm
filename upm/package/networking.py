import logging

log = logging.getLogger(__name__)


class NetworkOperator:
    def config_network(self, tree):
        pass


class NetworkOperatorBase(NetworkOperator):
    def __init__(self):
        self.networks = NetworkStructures()

    def config_network(self, iter):
        for node in iter:
            if node.height > 0:
                package_name = node.get_name()
                network_name = self.get_network_name(package_name)
                network = NetworkStructure(network_name)
                node.add_network_config(network_name, package_name)
                for child in node.children:
                    child.add_network_config(network_name, child.get_name())
                self.networks.add_network(network)
        return self.networks

    @staticmethod
    def get_network_name(name):
        return name + "_" + "network"


class NetworkStructures:
    def __init__(self):
        self.networks = []

    def add_network(self, network):
        self.networks.append(network)

    def to_dict(self):
        pass

    def to_compose(self):
        networks = {}
        for network in self.networks:
            networks.update(network.to_compose())
            log.debug(network)
        return networks


class NetworkStructure:
    def __init__(self, name, driver='bridge'):
        self.name = name
        self.driver = driver

    def to_dict(self):
        pass

    def get_name(self):
        return self.name

    def get_driver(self):
        return self.driver

    def to_compose(self):
        return {self.get_name(): {'driver': self.get_driver()}}
