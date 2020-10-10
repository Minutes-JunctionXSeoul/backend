import os
import math
import pandas as pd

from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from .datetime_extractor import process_datetime_str

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
    # documents = list(map(lambda x: x.lower(), documents))
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
            categories = ['Person', 'Location', 'Organization', 'Product','Address','PhoneNumber','Email','URL','DateTime']
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
                    extract_title(result.entities, 5 * i + idx)
                    extract_content(result.entities, 5 * i + idx)
                    sentence_list.append(iter_documents[idx])

        # print(title_list)
        # print(content_list)
        content_df = pd.DataFrame(content_list)
        title_df = pd.DataFrame(title_list)
        sentence_df = pd.DataFrame(sentence_list, columns=["memo"]).reset_index()

        df = pd.merge(title_df, content_df, on="index")
        df = pd.merge(df, sentence_df, on="index")

        #2개의 일이 하나의 일정에 겹친 경우
        change_datetime = []
        for x in range(1, len(df)):
            previous = df.iloc[x-1]
            current = df.iloc[x]
            if previous.loc['index'] == current.loc['index']:
                if pd.isna(previous.loc['DateTime']) and not pd.isna(current.loc['DateTime']):
                    duplicate_datetime = current.loc['DateTime']
                    change_datetime.append((x-1,duplicate_datetime))
                if not pd.isna(previous.loc['DateTime']) and pd.isna(current.loc['DateTime']):
                    duplicate_datetime = previous.loc['DateTime']
                    change_datetime.append((x,duplicate_datetime))
        for change in change_datetime:
            df.loc[change[0],'DateTime'] = change[1]

        #title이 추출되지 않는경우, 다른 object를 title로 올린다.
        #datetime밖에 추출되지 않는 경우, memo를 title로 올린다.
        change_title = []
        column = list(set(df.columns) - set(['index', 'title', 'DateTime', 'memo']))
        for x in range(len(df)):
            current = df.iloc[x]
            if current.loc['title'] == "":
                check = 0
                current_obj = current[column] # 다른 object 추출
                for title in current_obj:
                    if not pd.isna(title):
                        change_title.append((x, title))
                        check += 1
                if check == 0:
                    change_title.append((x, current['memo']))

        for change in change_title:
            df.loc[change[0], 'title'] = change[1]

        # apply date extraction to DateTime column
        for x in range(len(df)):
            try:
                parsed_datetime = process_datetime_str(df.loc[x, 'DateTime'])
                if parsed_datetime:
                    start_datetime, end_datetime = parsed_datetime
                else:
                    start_datetime, end_datetime = None, None
            except:
                start_datetime, end_datetime = None, None
                print("Error while parsing ", df.loc[x, 'DateTime'])
            df.loc[x, 'StartDateTime'] = start_datetime
            df.loc[x, 'EndDateTime'] = end_datetime

        # reformat to .ics format
        return df

    except Exception as err:
        print("Encountered exception. {}".format(err))
