def save_msg(user_name, text):
    try:
        # Читаем текущие данные (автоматически подтянет ссылку из [connections.gsheets])
        df = conn.read()
        
        # Создаем новую строчку
        new_row = pd.DataFrame([{
            "Дата": datetime.datetime.now().strftime("%d.%m %H:%M"),
            "Пользователь": user_name,
            "Сообщение": text,
            "Ответ": ""
        }])
        
        # Объединяем старое с новым
        updated_df = pd.concat([df, new_row], ignore_index=True)
        
        # Записываем обратно в облако
        conn.update(data=updated_df)
        return True
    except Exception as e:
        # Если снова будет ошибка, мы увидим её текст в логах
        print(f"DEBUG: {e}")
        return False
