
from langchain_community.tools import DuckDuckGoSearchRun
from langsmith import traceable


class GatherContext:
    @staticmethod
    @traceable(name="gathercontect")
    def gathercontext(topic , objectives ,  success):
        query = f"{topic} and our larning objctives {objectives} and success area {success}"
        search = DuckDuckGoSearchRun()
        respone = search.run({'query' : query})
        print(respone)
        return respone
