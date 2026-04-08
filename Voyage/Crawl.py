from abc import ABCMeta, abstractmethod


class Crawl(metaclass=ABCMeta):
    @abstractmethod
    def crawl(self, vessel, tracking_no):
        pass
