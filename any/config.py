import os

ANY_CACHE = os.path.join(os.environ['HOME'], ".any")
ANY_HOME = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


class Directory:
    @staticmethod
    def project(repository_id):
        """
        Path to the project root directory for the given repository_id.
        :param repository_id:
        :return:
        """
        path = os.path.join(ANY_CACHE, repository_id)
        os.makedirs(path, exist_ok=True)
        return path

    @staticmethod
    def repository(repository_id):
        """
        Path to the Git subdirectory for the given repository_id.
        :param repository_id:
        :return:
        """
        path = os.path.join(Directory.project(repository_id), "repository")
        os.makedirs(path, exist_ok=True)
        return path

    @staticmethod
    def environment(repository_id):
        """
        Path to the environment cache subdirectory for the given repository_id.
        For Poetry projects, this contains any virtualenvs used to build the project.
        :param repository_id:
        :return:
        """
        path = os.path.join(Directory.project(repository_id), "environment")
        os.makedirs(path, exist_ok=True)
        return path
