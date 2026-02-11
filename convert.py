import xml.etree.ElementTree as ET
import csv
import json
import os

def convert():
    seo_data = {}
    csv_file = 'Каталог 11-02-2026_15-42-17.csv'
    
    if not os.path.exists(csv_file):
        print(f"Ошибка: Файл {csv_file} не найден!")
        return

    # Пробуем разные кодировки (Windows-1251 — самая вероятная причина ошибки)
    encodings = ['windows-1251', 'utf-8-sig', 'utf-8', 'cp1251']
    success_encoding = None
    
    for enc in encodings:
        try:
            with open(csv_file, mode='r', encoding=enc) as f:
                content = f.read(1000) # Пробуем прочитать кусочек
                success_encoding = enc
                break
        except UnicodeDecodeError:
            continue

    if not success_encoding:
        print("Не удалось определить кодировку файла.")
        return

    print(f"Файл прочитан в кодировке: {success_encoding}")

    # Читаем данные
    with open(csv_file, mode='r', encoding=success_encoding) as f:
        reader = csv.reader(f, delimiter=';')
        next(reader, None)  # Пропуск заголовков
        
        for row in reader:
            if not row or len(row) < 5: continue
            
            # Чистим ID от кавычек и невидимых символов
            item_id = row[0].strip().replace('"', '')
            
            # Описания (9 - краткое, 10 - полное)
            short_t = row[9].strip().replace('""', '"').strip('"') if len(row) > 9 else ""
            full_t = row[10].strip().replace('""', '"').strip('"') if len(row) > 10 else ""
            
            # Выбираем лучшее описание
            final_desc = full_t if len(full_t) > 20 else short_t
            
            if item_id:
                seo_data[item_id] = {
                    'description': final_desc,
                    'title': row[11].strip().strip('"') if len(row) > 11 else "",
                    'seo_desc': row[12].strip().strip('"') if len(row) > 12 else ""
                }

    # Парсим XML
    tree = ET.parse('pricelist.xml')
    root = tree.getroot()
    shop = root.find('shop')

    categories = []
    for cat in shop.find('categories').findall('category'):
        categories.append({
            'id': cat.get('id'),
            'parentId': cat.get('parentId'),
            'name': cat.text
        })

    products = []
    found_desc_count = 0

    for offer in shop.find('offers').findall('offer'):
        oid = offer.get('id').strip()
        seo = seo_data.get(oid, {})
        
        desc = seo.get('description', '').strip()
        if desc:
            found_desc_count += 1
        else:
            desc = "Описание в процессе наполнения..."

        # Характеристики
        params = {p.get('name'): p.text for p in offer.findall('param')}

        products.append({
            'id': oid,
            'name': offer.find('name').text,
            'price': offer.find('price').text,
            'categoryId': offer.find('categoryId').text,
            'image': offer.find('picture').text if offer.find('picture') is not None else "",
            'description': desc,
            'seo_title': seo.get('seo_title', ''),
            'seo_desc': seo.get('seo_desc', ''),
            'params': params
        })

    # Сохраняем итоговый JSON
    with open('products.json', 'w', encoding='utf-8') as f:
        json.dump({'categories': categories, 'products': products}, f, ensure_ascii=False, indent=4)

    print(f"\n--- ИТОГОВЫЙ ОТЧЕТ ---")
    print(f"Всего товаров в XML: {len(products)}")
    print(f"Связано описаний: {found_desc_count}")

if __name__ == "__main__":
    convert()