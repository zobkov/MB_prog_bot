#!/bin/bash

# Скрипт для удобного запуска рассылки

echo "🤖 Система рассылки MB '25"
echo "=========================="
echo ""

# Проверка наличия основного CSV файла
if [ ! -f "broadcast.csv" ]; then
    echo "❌ Файл broadcast.csv не найден!"
    echo "Создайте файл с данными получателей перед запуском."
    exit 1
fi

echo "Выберите режим работы:"
echo "1) Dry-run (симуляция, безопасно)"
echo "2) Реальная отправка"
echo "3) Тест с тестовым файлом"
echo ""
read -p "Введите номер (1-3): " choice

case $choice in
    1)
        echo "🔍 Запуск в режиме симуляции..."
        python3 broadcast_script.py
        ;;
    2)
        echo "⚠️  ВНИМАНИЕ: Реальная отправка!"
        echo "Сообщения будут отправлены всем пользователям."
        read -p "Вы уверены? (y/N): " confirm
        if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
            python3 broadcast_script.py --send
        else
            echo "❌ Отменено пользователем."
        fi
        ;;
    3)
        if [ ! -f "test_broadcast.csv" ]; then
            echo "❌ Тестовый файл test_broadcast.csv не найден!"
            exit 1
        fi
        echo "🧪 Запуск с тестовыми данными..."
        python3 broadcast_script.py --csv test_broadcast.csv
        ;;
    *)
        echo "❌ Неверный выбор!"
        exit 1
        ;;
esac

echo ""
echo "✅ Завершено!"