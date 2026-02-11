import json
import os

def generate():
    # Настройки
    base_url = "https://taskem142-eng.github.io/mebel23"
    telegram_num = "+79002730150"
    
    if not os.path.exists('products.json'):
        print("Ошибка: Сначала запустите convert.py")
        return

    with open('products.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    products = data['products']
    if not os.path.exists('product'):
        os.makedirs('product')

    sitemap_links = [f"{base_url}/index.html"]

    template = """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{seo_title}</title>
        <meta name="description" content="{seo_desc}">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {{ background: #f8f9fa; padding: 40px 0; }}
            .card-product {{ background: #fff; border-radius: 15px; border: none; box-shadow: 0 5px 20px rgba(0,0,0,0.05); overflow: hidden; }}
            .img-side {{ background: #fff; padding: 30px; border-right: 1px solid #f0f0f0; display: flex; align-items: center; justify-content: center; }}
            .price {{ font-size: 2.5rem; font-weight: 800; color: #0088cc; }}
            .param-row {{ display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px dashed #eee; }}
        </style>
    </head>
    <body>
        <div class="container">
            <a href="../index.html" class="btn btn-outline-secondary mb-4">← Вернуться в каталог</a>
            <div class="card-product row g-0">
                <div class="col-md-5 img-side">
                    <img src="{image}" class="img-fluid" alt="{name}" style="max-height: 450px;">
                </div>
                <div class="col-md-7 p-5">
                    <h1 class="fw-bold">{name}</h1>
                    <div class="price my-4">{price} ₽</div>
                    
                    <div class="mb-4">
                        <h5>Характеристики:</h5>
                        {params_html}
                    </div>

                    <a href="https://t.me/{telegram}?text={msg}" class="btn btn-info btn-lg w-100 text-white shadow" style="background: #0088cc; border: none;">
                        Заказать в Telegram
                    </a>
                </div>
                <div class="col-12 p-5 bg-light border-top">
                    <h4>Описание товара</h4>
                    <div class="mt-3" style="line-height: 1.8; color: #555;">{description}</div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    for p in products:
        params_html = "".join([f"<div class='param-row'><span>{k}</span><b>{v}</b></div>" for k, v in p['params'].items()])
        
        msg = f"Здравствуйте! Хочу заказать товар: {p['name']} (ID: {p['id']})"
        
        content = template.format(
            name=p['name'],
            price=p['price'],
            image=p['image'],
            description=p['description'],
            seo_title=p['seo_title'] or p['name'],
            seo_desc=p['seo_desc'] or p['name'],
            params_html=params_html,
            telegram=telegram_num.replace('+', ''),
            msg=msg.replace(' ', '%20')
        )

        with open(f"product/{p['id']}.html", 'w', encoding='utf-8') as f:
            f.write(content)
        
        sitemap_links.append(f"{base_url}/product/{p['id']}.html")

    # Sitemap
    with open('sitemap.xml', 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for link in sitemap_links:
            f.write(f'  <url><loc>{link}</loc></url>\n')
        f.write('</urlset>')

    print(f"Готово! Создано страниц: {len(products)} и sitemap.xml")

if __name__ == "__main__":
    generate()