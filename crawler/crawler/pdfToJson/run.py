import json
from crawler.pdfToJson.pdfClient import grobid_client


def get_content(pdf_path):
    config_path = './crawler/pdfToJson/config.json'
    pdfClient = grobid_client(config_path=config_path)
    jsonData = pdfClient.process_pdf(pdf_path)
    return jsonData


if __name__ == "__main__":
    try:
        pdf_path = './1.pdf'
        jsonData = get_content(pdf_path)

        title = jsonData["title"]
        authors = jsonData["authors"]
        keywords = jsonData["keywords"]
        abstract = jsonData["abstract"]
        paperContent = jsonData["paperContent"]
        references = jsonData["references"]

        print("finish " + pdf_path)
    except Exception as e:
        print(e)
        print("error " + pdf_path)
    else:
        with open("./1.json", "w", encoding="utf-8") as fout:
            output = json.dumps(jsonData, ensure_ascii=False,
                                indent=2, separators=(',', ': '))
            fout.write(output)
