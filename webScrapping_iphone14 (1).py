import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re

# Listas para almacenar los datos
titles = []
prices_previous = []
prices_currents = []
califications = []
reviews = []
full_shipping = []
conditions = []
discounts = []

# Definir Numero de datos
data_size = 100

# Función para realizar scraping en una página
def scrape_page(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises an error for bad responses
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extraer contenedores de productos
        items = soup.find_all('li', class_='ui-search-layout__item')
        
        for item in items:
            # Título del producto
            title = item.find('h2', class_='poly-box poly-component__title')
            title_text = title.text.strip() if title else "N/A"
            
            # Precio previo de descuento del producto
            # Encuentra el primer span con esa clase, que es el precio previo
            price_previous = item.find('span', class_='andes-money-amount__fraction')
            price_previous_text = price_previous.text.replace(',', '') if price_previous else "0"
            
            # Descuento del producto
            discount = item.find('span', class_='andes-money-amount__discount')
            discount_text = discount.text if discount else "0"
            discount_number = re.search(r'\d+', discount_text).group() if discount_text else "0"
            
            # Calcular precio actual con el descuento
            price_current = int(int(price_previous_text) - (int(price_previous_text) * int(discount_number) / 100))
            
            # Calificacion del producto
            calification = item.find('span', class_='poly-reviews__rating')
            calification_text = calification.text.strip() if calification else "N/A"
            
            # Reseñas del productos
            review = item.find('span', class_='poly-reviews__total')
            review_text = review.text.strip('()') if review else "N/A"
            
            # Condicion del producto
            condition = item.find('span', class_='poly-component__item-condition')
            condition_text = condition.text.strip() if condition else "Nuevo"
            
            # Verificar si hay datos válidos antes de agregar
            if title_text != "N/A" and price_previous_text.isdigit() and calification_text != "N/A" and review_text != "N/A":
                titles.append(title_text)
                prices_previous.append(int(price_previous_text))
                prices_currents.append(price_current)
                califications.append(calification_text)
                reviews.append(review_text)
                conditions.append(condition_text)
                discounts.append(int(discount_number))
                
                # Check for Full Shipping
                full = item.find('span', class_='poly-component__shipped-from')
                full_text = "1" if full else "0"
                full_shipping.append(full_text)

    except requests.RequestException as e:
        print(f"Error fetching data from {url}: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Scraping de múltiples páginas hasta obtener al menos 100 registros
page = 1
while len(titles) < data_size:
    url = f"https://listado.mercadolibre.com.mx/iphone-14#pagination={page}"
    print(f"Scraping página {page}...")
    scrape_page(url)
    page += 1
    time.sleep(2)  # Pausa de 1 segundo entre páginas para evitar ser bloqueado

# Crear un DataFrame con los datos recolectados
df = pd.DataFrame({
    'Titulo': titles,
    'Precio previo': prices_previous,
    'Descuento': discounts,
    'Precio actual': prices_currents,
    'Calificacion': califications,
    'Reseñas': reviews,
    'Envio Full': full_shipping,
    'Condicion': conditions
})

# Asegurarse de que el DataFrame tenga al menos 100 registros
df = df.head(data_size)

# Mostrar las primeras filas del DataFrame
print("\nPrimeras filas del DataFrame:")
print(df.head())

# Guardar en un archivo CSV solo si hay datos válidos
csv_file = 'capturas_pantalla.csv'
if not df.empty:
    df.to_csv(csv_file, index=False)
    print(f"Datos guardados en {csv_file}.")
else:
    print("No hay datos válidos para guardar.")
