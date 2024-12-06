import json
import pandas as pd

class Url_Sheets:
    def __init__(self):
        self.url = 'https://docs.google.com/spreadsheets/d/1PBwyM79jZS7b4GxSr1ayocGleWT48k9V/'
    def nomes_ids(self):
        df = pd.read_csv(self.url + 'export?gid=268641735&range=A:B&format=csv')
        pd.set_option('display.max_columns', None)
        return dict(zip(df['NOME'], df['ID']))


    def titulos(self):
        dic_nomes = self.nomes_ids()
        with open('nomes_psicos.json', 'w', encoding='utf-8') as arquivo:
            json.dump(dic_nomes, arquivo, indent=4, ensure_ascii=False)
        return dic_nomes.keys()

    def planilha(self, psico:str):
        dic = self.nomes_ids()
        id = dic[psico]
        df = pd.read_csv(self.url + f'export?gid={id}&range=A:F&format=csv')
        df.fillna(value=pd.NA, inplace=True)
        df.to_csv(f'agenda_{psico}.csv', sep=';', decimal=',', index=False, header=True, encoding='utf-8')
        return df