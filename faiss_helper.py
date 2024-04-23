# *_* encoding: utf-8 *_*
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings
import os,dotenv
from langchain_core.documents import Document
dotenv.load_dotenv()
embeddings = OllamaEmbeddings(     
    model="milkey/m3e"
)



# member_openid 为用户的 编号
class FaissVectorManager:
    def __init__(self, member_openid):
        # 如果没有用户目录则新建
        self.member_openid = member_openid
        self.dir = f'./faiss/{member_openid}'
        if not os.path.exists(self.dir):
            os.makedirs(self.dir)
            texts=["init"]
            text_embeddings = embeddings.embed_documents(texts)
            text_embedding_pairs = zip(texts, text_embeddings)
            faiss = FAISS.from_embeddings(text_embedding_pairs, embeddings)
            faiss.save_local(self.dir)
            self.faiss=faiss
        else:
            self.faiss = FAISS.load_local(self.dir,embeddings,allow_dangerous_deserialization   = True)
        

    def save(self):
        self.faiss.save_local(self.dir)

    def add(self, text):
        self.faiss.add_documents(  [Document(page_content=text),] )
        self.save()


    def search(self, text, top_k=5):
        return self.faiss.similarity_search_with_score(text, top_k)

    def delete(self, text):
        #通过搜索出的id,返回需删除的id
        result  = self.faiss.similarity_search_with_score(text, 1)
        print(result)

def main():
    manager = FaissVectorManager('123')
    # manager.add('记住，你叫猫局')
    
    testresult = manager.search('记住，你叫猫？')
    for i in testresult:
        print(i)

if __name__ == '__main__':
    main()

