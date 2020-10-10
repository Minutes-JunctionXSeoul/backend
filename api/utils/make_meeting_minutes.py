import docx
import numpy
from datetime import datetime

from .log_summary import extract_keywords
from .calendar_utils import df_to_ics
from .entity_extractor import extract_entities

def make_docx(client,documents):
    doc = docx.Document()
    
    today = datetime.now()
    date = str(today.year)+str(today.month)+str(today.day)+"_"+str(today.hour)+str('%02d' % today.minute)

    #title
    doc.add_heading(date+" summary",0)
    para = doc.add_paragraph()

    def write_subtitle(string,para):
        title = para.add_run(string+"\n")
        title.bold = True
        title.font.size = docx.shared.Pt(20)

    def write_keyword(summary_dict,para):
        for key, value in summary_dict.items():
            keyword = para.add_run(key+" / ")
            keyword.bold = True
            keyword.font.size = docx.shared.Pt(15)
        para.add_run("\n\n")

    def write_summary(doc,summary,para):
        keyword_in_sentence = list(summary.values())
        keywords = list(summary.keys())
        for i in range(len(doc)):
            if doc[i] in keyword_in_sentence:
                keyword_in_sentence = numpy.array(keyword_in_sentence)
                idx = numpy.where(keyword_in_sentence == doc[i])[0]
                write_kw = ""
                for k in idx:
                    write_kw += keywords[k]+" / "
                keyword = para.add_run(write_kw[:-2])
                para.add_run("\n")
                keyword.bold = True
                keyword.font.size = docx.shared.Pt(15)
            sentence = para.add_run(doc[i])
            para.add_run("\n")


    def write_todo(df,para):
        for i in range(len(df)):
            current = df.iloc[i]
            start_date = current['Start Date']
            start_time = current['Start Time']
            end_date = current['End Date']
            end_time = current['End Time']
            subject = current['Subject']
            description = current['Description']
            result = f'[{start_date} {start_time} ~ {end_date} {end_time}] {subject} \norigin message: {description}\n'
            todo = para.add_run(result+"\n")


    keyword_sentence_dict = extract_keywords(client,documents)
    df = extract_entities(client, documents)
    write_subtitle("Keyword",para)
    write_keyword(keyword_sentence_dict,para)
    todo_df = df_to_ics(df)  
    if not todo_df.empty:
        write_subtitle("To-Do List",para)
        write_todo(df_to_ics(df),para)
    write_subtitle("Log",para)
    write_summary(documents,keyword_sentence_dict,para)
    para.add_run("\n\n")
    
    file_name = date + '_meeting minutes.docx'
    doc.save(file_name)
    return file_name
    

