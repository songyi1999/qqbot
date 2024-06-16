import  dotenv
from langchain_community.llms import QianfanLLMEndpoint
dotenv.load_dotenv()


llm = QianfanLLMEndpoint(model_name="ERNIE-Speed-8K")
res = llm.invoke("鲁迅为啥要打周树人？")
print(res)


