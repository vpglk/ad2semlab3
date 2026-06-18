import streamlit as st

from analytics import (
    read_dataset,
    get_dataset_info,
    get_column_types,
    get_numeric_summary,
    get_categorical_summary,
    create_basic_charts,
    prepare_summary_for_llm,
)

from agent import generate_report


st.set_page_config(
    page_title="LLM-аналитика событий на карте",
    layout="wide"
)

st.title("LLM-аналитика событий на карте")

st.write(
    "Приложение анализирует датасет с городскими событиями на карте. "
    "Пользователь загружает CSV или Excel-файл, после чего система показывает "
    "метрики, графики и формирует аналитический отчет через LLM-агента."
)

uploaded_file = st.file_uploader(
    "Загрузите файл с событиями",
    type=["csv", "xlsx", "xls"]
)

user_instruction = st.text_area(
    "Инструкция для анализа",
    value="""Проанализируй события на карте города.
Определи:
- наиболее частые категории событий;
- районы с наибольшим количеством происшествий;
- количество событий высокого приоритета;
- потенциально проблемные районы;
- основные закономерности в данных;
- рекомендации для городских служб.
Сформируй подробный аналитический отчет.""",
    height=220
)

if uploaded_file is not None:
    try:
        df = read_dataset(uploaded_file)

        st.subheader("Предпросмотр данных")
        st.dataframe(df.head(30), use_container_width=True)

        required_columns = [
            "id",
            "event_description",
            "category",
            "district",
            "priority"
        ]

        missing_required = [
            column for column in required_columns
            if column not in df.columns
        ]

        if missing_required:
            st.warning(
                "В датасете отсутствуют ожидаемые столбцы: "
                + ", ".join(missing_required)
            )
        else:
            st.success("Файл соответствует ожидаемой структуре датасета событий.")

        info = get_dataset_info(df)

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Количество строк", info["rows"])
        col2.metric("Количество столбцов", info["columns"])
        col3.metric("Пропущенные значения", info["missing_values"])
        col4.metric("Дубликаты", info["duplicates"])

        if "priority" in df.columns:
            high_priority_count = df[
                df["priority"].astype(str).str.lower() == "высокая"
            ].shape[0]

            st.metric(
                "События высокого приоритета",
                high_priority_count
            )

        st.subheader("Графики")

        charts = create_basic_charts(df)

        if charts:
            chart_columns = st.columns(len(charts))

            for index, fig in enumerate(charts):
                fig.update_layout(
                    height=350,
                    margin=dict(l=10, r=10, t=50, b=30)
                )

                with chart_columns[index]:
                    st.plotly_chart(
                        fig,
                        use_container_width=True
                    )
        else:
            st.info(
                "Для данного датасета не удалось автоматически построить графики."
            )

        st.subheader("LLM-отчет агента")

        st.write(
            "После нажатия кнопки Python-инструменты подготовят сводку по данным, "
            "а LLM-агент сформирует аналитический отчет."
        )

        if st.button("Сгенерировать отчет"):
            with st.spinner("Агент анализирует данные и формирует отчет..."):
                dataset_summary = prepare_summary_for_llm(df)
                report = generate_report(
                    dataset_summary,
                    user_instruction
                )
                st.markdown(report)

    except Exception as e:
        st.error(f"Ошибка при обработке файла: {e}")

else:
    st.info("Загрузите файл `events.csv`, чтобы начать анализ.")