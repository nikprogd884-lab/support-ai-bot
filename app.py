# Находим функцию save_support_msg и заменяем её полностью:
def save_support_msg(user_id, text):
    try:
        # 1. Генерируем ссылку для прямого скачивания CSV из твоей таблицы
        sheet_id = "1oc_E2IHKjJZSjt9fscY93srN77sNeN4qjqFrP4QkRN0"
        export_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        
        # 2. Читаем текущие данные
        df = pd.read_csv(export_url)
        
        # 3. Добавляем новую строку
        new_row = pd.DataFrame([{
            "Дата": datetime.datetime.now().strftime("%d.%m %H:%M"), 
            "Пользователь": user_id, 
            "Сообщение": text, 
            "Ответ": ""
        }])
        
        updated_df = pd.concat([df, new_row], ignore_index=True)
        
        # 4. Пробуем записать через коннектор (теперь он должен сработать, так как структура совпадает)
        conn.update(spreadsheet=st.secrets["GSHEET_URL"], data=updated_df)
        st.success("Сообщение улетело в базу!")
    except Exception as e:
        st.error(f"Ошибка синхронизации: {e}")
