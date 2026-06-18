import pandas as pd
import plotly.express as px


def read_dataset(uploaded_file):
    file_name = uploaded_file.name.lower()

    if file_name.endswith(".csv"):
        return pd.read_csv(uploaded_file)

    if file_name.endswith(".xlsx") or file_name.endswith(".xls"):
        return pd.read_excel(uploaded_file)

    raise ValueError("Поддерживаются только CSV и Excel файлы.")


def get_dataset_info(df: pd.DataFrame) -> dict:
    return {
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "column_names": list(df.columns),
        "missing_values": int(df.isna().sum().sum()),
        "duplicates": int(df.duplicated().sum()),
    }


def get_column_types(df: pd.DataFrame) -> pd.DataFrame:
    data = []

    for column in df.columns:
        data.append({
            "Столбец": column,
            "Тип данных": str(df[column].dtype),
            "Пропуски": int(df[column].isna().sum()),
            "Уникальные значения": int(df[column].nunique())
        })

    return pd.DataFrame(data)


def get_numeric_summary(df: pd.DataFrame) -> pd.DataFrame:
    numeric_df = df.select_dtypes(include="number")

    if numeric_df.empty:
        return pd.DataFrame()

    return numeric_df.describe().T


def get_categorical_summary(df: pd.DataFrame) -> dict:
    result = {}

    categorical_columns = df.select_dtypes(include=["object", "category"]).columns

    for column in categorical_columns:
        result[column] = df[column].value_counts().head(10).reset_index()
        result[column].columns = [column, "Количество"]

    return result



def create_basic_charts(df):
    import plotly.express as px

    charts = []

    if "category" in df.columns:
        category_counts = df["category"].value_counts().reset_index()
        category_counts.columns = ["Категория", "Количество"]

        charts.append(
            px.bar(
                category_counts,
                x="Категория",
                y="Количество",
                title="Количество событий по категориям"
            )
        )

    if "district" in df.columns:
        district_counts = df["district"].value_counts().reset_index()
        district_counts.columns = ["Район", "Количество"]

        charts.append(
            px.bar(
                district_counts,
                x="Район",
                y="Количество",
                title="Количество событий по районам"
            )
        )

    if "priority" in df.columns:
        priority_counts = df["priority"].value_counts().reset_index()
        priority_counts.columns = ["Приоритет", "Количество"]

        charts.append(
            px.pie(
                priority_counts,
                names="Приоритет",
                values="Количество",
                title="Распределение по приоритету"
            )
        )

    return charts

def prepare_summary_for_llm(df: pd.DataFrame) -> str:
    info = get_dataset_info(df)
    column_types = get_column_types(df)

    text = []
    text.append(f"Количество строк: {info['rows']}")
    text.append(f"Количество столбцов: {info['columns']}")
    text.append(f"Пропущенные значения: {info['missing_values']}")
    text.append(f"Дубликаты: {info['duplicates']}")
    text.append(f"Названия столбцов: {', '.join(info['column_names'])}")
    text.append("\nТипы столбцов:")
    text.append(column_types.to_string(index=False))

    numeric_summary = get_numeric_summary(df)
    if not numeric_summary.empty:
        text.append("\nСтатистика по числовым столбцам:")
        text.append(numeric_summary.to_string())

    categorical_summary = get_categorical_summary(df)
    if categorical_summary:
        text.append("\nТоп значений по категориальным столбцам:")
        for column, table in categorical_summary.items():
            text.append(f"\nСтолбец: {column}")
            text.append(table.to_string(index=False))

    sample = df.head(10).to_string(index=False)
    text.append("\nПервые 10 строк датасета:")
    text.append(sample)

    return "\n".join(text)