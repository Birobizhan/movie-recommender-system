with open('movies_with_all_info/check.csv', 'rb') as f:
    data = f.read()

# Попробуем декодировать вручную
try:
    text = data.decode('utf-8')
    print("✅ Файл успешно декодирован как UTF-8")
except UnicodeDecodeError as e:
    print("❌ Ошибка при декодировании UTF-8:", e)