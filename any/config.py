import os

ANY_CACHE = os.path.join(os.environ['HOME'], ".any")
ANY_KUBECONFIG = os.getenv("ANY_KUBECONFIG", os.getenv("KUBECONFIG"))


class Directory:
    @staticmethod
    def root(organization, repository):
        """
        Path to the directory of the given repository.
        :param organization:
        :param repository:
        :return:
        """
        path = os.path.join(ANY_CACHE, organization, repository)
        os.makedirs(path, exist_ok=True)
        return path
