import math 

from collections import Counter
from .entity_extractor import get_auth_client

# documents must be a list
def extract_keywords(client, documents):
    keywords_list = []
    try:
        n_iter = math.ceil(len(documents) / 5)
        for i in range(n_iter):
            if i == n_iter - 1:
                iter_documents = documents[5*i:]
            else:
                iter_documents = documents[5*i:5*(i+1)]
            responses = client.extract_key_phrases(documents = iter_documents)
            for idx, response in enumerate(responses):
                keywords_in_sentence = []
                if not response.is_error:
                    for phrase in response.key_phrases:
                        keywords_in_sentence.append(phrase)
                else:
                    print(response.id, response.error)
                keywords_list.append(keywords_in_sentence)

        #keyword 중에서 common한 것 num개 리턴
        def common_keywords_extraction(keywords_list, num = len(documents)//4):        
            keywords_count = collections.Counter(sum(keywords_list, []))
            common_keywords = keywords_count.most_common(num)
            result_keyword = []
            for i in range(num):
                result_keyword.append(common_keywords[i][0])
            return result_keyword

        #common keyword가 있는 문장과 키워드를 매핑
        def keyword_in_sentence(common_keyword, documents):
            keyword_sentence = dict()
            for sentence in documents:
                for keyword in common_keyword:
                    if(keyword in sentence):
                        if(keyword in keyword_sentence):
                            pass
                        else:
                            keyword_sentence[keyword] = sentence
            return keyword_sentence

        common_keyword_list = common_keywords_extraction(keywords_list)    
        result_summary = keyword_in_sentence(common_keyword_list, documents)
        
        return result_summary

    except Exception as err:
        print("Encountered exception. {}".format(err))
