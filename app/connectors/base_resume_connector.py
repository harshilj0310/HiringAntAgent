from abc import ABC, abstractmethod

class BaseResumeConnector(ABC):

    @abstractmethod
    def fetch_resumes(self) -> list:
        """Return a list of resume documents (dicts)."""
        pass

    @abstractmethod
    def fetch_resume_file(self, file_id) -> tuple[str, bytes] | None:
        """Given a file identifier, return (filename, file_content)."""
        pass