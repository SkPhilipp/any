import os

ANY_CACHE = os.path.join(os.environ['HOME'], ".any")
ANY_KUBECONFIG = os.getenv("ANY_KUBECONFIG", os.getenv("KUBECONFIG"))


class Directory:
    @staticmethod
    def root(organization, repository):
        """
        Path to the root directory for the given repository.
        :param organization:
        :param repository:
        :return:
        """
        path = os.path.join(ANY_CACHE, organization, repository)
        os.makedirs(path, exist_ok=True)
        return path

    @staticmethod
    def repository(organization, repository):
        """
        Path to the Git subdirectory for the given repository.
        :param organization:
        :param repository:
        :return:
        """
        path = os.path.join(Directory.root(organization, repository), "repository")
        os.makedirs(path, exist_ok=True)
        return path

    @staticmethod
    def environment(organization, repository):
        """
        Path to the environment cache subdirectory for the given repository.
        For Poetry projects, this contains any virtualenvs used to build the project.
        :param organization:
        :param repository:
        :return:
        """
        path = os.path.join(Directory.root(organization, repository), "environment")
        os.makedirs(path, exist_ok=True)
        return path
