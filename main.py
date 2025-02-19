import pandas as pd
import tkinter as tk
from tkinter import filedialog


def parse_title_row(row):
    """
    Processa uma linha do CSV no formato:
      Título,"Data"
    Remove delimitadores extras, separa o título e a data,
    e marca como 'série' se encontrar "Temporada", "Capítulo" ou "Episódio".
    """
    if not isinstance(row, str):
        row = str(row) if pd.notnull(row) else ""
    # Remove tudo a partir do primeiro ";" para eliminar delimitadores extras
    row = row.split(";")[0]
    # Divide a string na primeira vírgula
    parts = row.split(",", 1)
    if len(parts) == 2:
        title = parts[0].strip()
        date_str = parts[1].strip().strip('"')
    else:
        title = row.strip()
        date_str = ""
    # Converte para minúsculas para fazer a comparação sem case sensitive
    lower_title = title.lower()
    if "temporada" in lower_title or "capítulo" in lower_title or "episódio" in lower_title:
        detected_type = "série"
    else:
        detected_type = None
    return {"title": title, "date": date_str, "detected_type": detected_type}



def determine_type(row, prefix_counts):
    """
    Define o tipo com base em:
    - Se o parse inicial já detectou "série" (por 'Temporada' ou 'Capítulo'), usa isso.
    - Caso contrário, extrai o prefixo (parte antes do primeiro ":") e, se esse prefixo aparecer mais de uma vez, define como "série".
    """
    if row.get("detected_type") == "série":
        return "série"
    title = row.get("title", "")
    if ":" in title:
        prefix = title.split(":", 1)[0].strip()
    else:
        prefix = title.strip()
    if prefix_counts.get(prefix, 0) > 1:
        return "série"
    return "filme"


def select_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Selecione um arquivo CSV",
        filetypes=[("Arquivos CSV", "*.csv")]
    )
    return file_path


def main():
    file_path = select_file()
    if not file_path:
        print("Nenhum arquivo selecionado.")
        return

    try:
        # Lê o CSV usando vírgula como delimitador e somente a primeira coluna
        df = pd.read_csv(file_path, delimiter=",", header=0, usecols=[0])
        print("Colunas encontradas:", df.columns.tolist())
        df = df.rename(columns={df.columns[0]: "TitleDate"})

        # Aplica a função de parsing para separar título e data
        parsed = df["TitleDate"].apply(parse_title_row)
        parsed_df = pd.DataFrame(parsed.tolist())

        # Converte a coluna "date" para datetime (formato m/d/yy)
        parsed_df["date"] = pd.to_datetime(parsed_df["date"], format="%m/%d/%y", errors="coerce")

        # Calcula os prefixos (parte antes do primeiro ":") e suas frequências
        prefix_counts = {}
        for title in parsed_df["title"]:
            if ":" in title:
                prefix = title.split(":", 1)[0].strip()
            else:
                prefix = title.strip()
            prefix_counts[prefix] = prefix_counts.get(prefix, 0) + 1

        # Define o tipo usando a heurística (detected_type ou contagem de prefixo)
        parsed_df["type"] = parsed_df.apply(lambda row: determine_type(row, prefix_counts), axis=1)

        # Separa os dados em dois DataFrames: filmes e séries
        films_df = parsed_df[parsed_df["type"] == "filme"]
        series_df = parsed_df[parsed_df["type"] == "série"]

        # Salva os CSVs usando ";" como delimitador e codificação utf-8-sig
        output_films = file_path.replace(".csv", "_films.csv")
        output_series = file_path.replace(".csv", "_series.csv")
        films_df.to_csv(output_films, sep=";", index=False, encoding="utf-8-sig")
        series_df.to_csv(output_series, sep=";", index=False, encoding="utf-8-sig")

        print(f"Arquivo de filmes salvo em: {output_films}")
        print(f"Arquivo de séries salvo em: {output_series}")
        print("Exemplo de dados processados (Filmes):")
        print(films_df.head())
        print("Exemplo de dados processados (Séries):")
        print(series_df.head())

    except Exception as e:
        print(f"Erro ao processar o arquivo: {e}")


if __name__ == '__main__':
    main()
