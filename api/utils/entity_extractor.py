import os
import math
import pandas as pd

from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

def get_auth_client():
    key = os.environ['NER_KEY']
    endpoint = os.environ['NER_ENDPOINT']
    ta_credential = AzureKeyCredential(key)
    text_analytics_client = TextAnalyticsClient(
            endpoint=endpoint, 
            credential=ta_credential)
    return text_analytics_client

# documents must be a list
def extract_entities(client, documents):
    documents = list(map(lambda x: x.lower(), documents))
    title_list, content_list, sentence_list = [], [], []

    def extract_title(entities, i):
        result = {'index' : i}
        title = ""
        for entity in entities:
            if (entity.category in ["Skill", "Event"]):
                title += entity.text
                title += '_'
        result['title'] = title[:-1]
        title_list.append(result)

    def extract_content(entities, i):
        result = {'index' : i}
        for entity in entities:
            categories = ['Person','Location', 'Organization', 'Product','Address','PhoneNumber','Email','URL','DateTime']
            if entity.category in categories:
                if entity.category in result:
                    content_list.append(result)
                    result = {'index' : i}
            result[entity.category] = entity.text
        content_list.append(result)

    try:
        n_iter = math.ceil(len(documents) / 5)
        for i in range(n_iter):
            if i == n_iter - 1:
                iter_documents = documents[5*i:]
            else:
                iter_documents = documents[5*i:5*(i+1)]
            results = client.recognize_entities(documents=iter_documents)
            for idx, result in enumerate(results):
                # extract only if the document contains DateTime Entity
                contains_datetime = False
                for entity in result.entities:
                    if entity['category'] == 'DateTime':
                        contains_datetime = True
                        break
                if contains_datetime:
                    extract_title(result.entities, idx)
                    extract_content(result.entities, idx)
                    sentence_list.append(documents[idx])

        # print(title_list)
        # print(content_list)
        content_df = pd.DataFrame(content_list)
        title_df = pd.DataFrame(title_list)
        sentence_df = pd.DataFrame(sentence_list, columns=["memo"]).reset_index()

        df = pd.merge(title_df, content_df, on="index")
        df = pd.merge(df, sentence_df, on="index")
        print(df)

        return df.to_dict('records')

    except Exception as err:
        print("Encountered exception. {}".format(err))
