from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
import calendar
import json

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    angle_result = None
    
    if request.method == 'POST':
        # Проверяем, какая форма была отправлена
        if 'datetime' in request.form and request.form['datetime'].strip():
            try:
                input_str = request.form['datetime'].strip()
                parts = input_str.split()
                if len(parts) != 2:
                    raise ValueError("Неверный формат. Используйте: DD.MM HH")
                date_part, time_part = parts
                day, month = date_part.split('.')
                if len(day) != 2 or len(month) != 2:
                    raise ValueError("Дата должна быть в формате DD.MM")
                day = int(day)
                month = int(month)
                hour = int(time_part)

                current = datetime(2026, month, day, hour, 0, 0)
                year_start = datetime(2026, 3, 21, 0, 0, 0)

                # Расчёт часов
                year_hours = (current - year_start).total_seconds() / 3600
                month_start = datetime(current.year, current.month, 1, 0, 0, 0)
                month_hours = (current - month_start).total_seconds() / 3600
                week_start = current - timedelta(days=current.weekday())
                week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
                week_hours = (current - week_start).total_seconds() / 3600

                _, days_in_month = calendar.monthrange(current.year, current.month)
                month_total = days_in_month * 24

                # Расчёты
                year_ratio = year_hours / 8760
                month_ratio = month_hours / month_total
                week_ratio_5 = week_hours / 120
                week_ratio_7 = week_hours / 168

                year_120 = year_ratio * 120
                year_168 = year_ratio * 168
                year_24 = year_ratio * 24
                year_month = year_ratio * month_total

                month_120 = month_ratio * 120
                month_168 = month_ratio * 168
                month_24 = month_ratio * 24

                week_24_5 = week_ratio_5 * 24
                week_24_7 = week_ratio_7 * 24

                result = {
                    'year_hours': round(year_hours, 0),
                    'week_hours': round(week_hours, 0),
                    'month_hours': round(month_hours, 0),
                    'year_values': [round(year_120, 2), round(year_168, 2), round(year_24, 2), round(year_month, 2)],
                    'month_values': [round(month_120, 2), round(month_168, 2), round(month_24, 2)],
                    'week_values': [round(week_24_5, 2), round(week_24_7, 2)]
                }
                
                # Если это AJAX запрос, возвращаем JSON
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'result': result})
                    
            except Exception as e:
                result = {'error': str(e)}
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'result': result})
        
        # Обработка ANGLE CALCULATOR
        elif 'price' in request.form and request.form['price'].strip():
            try:
                price_str = request.form['price'].replace(',', '.')
                cells_str = request.form['cells'].replace(',', '.')
                
                price = float(price_str)
                cells = float(cells_str)
                
                if cells == 0:
                    raise ValueError("Кол-во ячеек не может быть 0")
                
                # Основной расчёт: цена / ячейки / ячейки
                base_value = price / cells / cells
                
                # Умножение на 1.5, 2, 3, 4, 5, 6, 7, 8
                multipliers = [1.5, 2, 3, 4, 5, 6, 7, 8]
                multiply_results = [round(base_value * m, 4) for m in multipliers]
                
                # Деление на 1.5, 2, 3, 4, 5, 6, 7, 8
                divide_results = [round(base_value / m, 4) for m in multipliers]
                
                angle_result = {
                    'base_value': round(base_value, 4),
                    'multiply_results': multiply_results,
                    'divide_results': divide_results,
                    'multipliers': multipliers
                }
                
                # Если это AJAX запрос, возвращаем JSON
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'angle_result': angle_result})
                    
            except ValueError as e:
                angle_result = {'error': str(e)}
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'angle_result': angle_result})
            except Exception as e:
                angle_result = {'error': 'Ошибка в расчётах: ' + str(e)}
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'angle_result': angle_result})

    return render_template('index.html', result=result, angle_result=angle_result)

if __name__ == '__main__':
    app.run(debug=True)
