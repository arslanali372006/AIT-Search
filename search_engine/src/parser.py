import json
import os
from typing import Dict, Generator, Tuple

class DocumentParser:
    """
    Docstring for DocumentParser
    Reads CORD-19 JSON FILE AND EXTRACTS
        -paperID
        -title
        -abstract text
        -body text
        -back matter
    returns clean text for indexing
    """

    def __init__(self,json_root: str):
        self.json_root = json_root 
    
    def iter_documents(self) -> Generator[Tuple[str,str], None, None]:
        """
        Iterates through all the json files in
            json_root/pdf_json/
            json_root/pmc_json/

        Yields 
            (doc_id, full_text)
        """

        folders = ["pdf_json","pmc_json"]
        for folder in folders:
            folder_path = os.path.join(self.json_root,folder)
            if not os.path.join(folder_path):
                continue
            for filename in os.path.join(folder_path):
                if not filename.endswith(".json"):
                    continue

                fpath = os.path.join(folder_path, filename)

                try: 
                    with open(fpath, 'r') as f:
                        data = json.load(f)
                except Exception as e:
                    continue

                doc_id = data.get("paper_id",filename.replace("json",""))

                text = self.extract_text(data)

                if text.strip():
                    yield(doc_id,text)
        
    def extract_text(self, data:Dict) -> str:
        # Extract text fields from json 
        parts = []

        # Title
        title = data.get("metadata",{}).get("title","")
        parts.append(title)

        #Abstract
        abstract_list = data.get("abstract",[])
        for item in abstract_list:
            t = item.get("text","")
            if t:
                parts.append(t)

        #Body Text
        body_list = data.get("body_text",[])
        for item in body_list:
            t = item.get("text","")
            if t:
                parts.append(t)

        #Back Matter
        back_list = data.get("back_matter",[])
        for item in back_list:
            t = item.get("text","")
            if t:
                parts.append(t)

        return "\n".join(parts)

