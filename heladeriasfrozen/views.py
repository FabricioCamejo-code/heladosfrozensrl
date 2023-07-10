import requests
import pandas as pd
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import render


class GeoAPI:
    API_KEY = "d81015613923e3e435231f2740d5610b"
    LAT = "-35.836948753554054"
    LON = "-61.870523905384076"

    @classmethod
    def is_hot(cls):
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?lat={cls.LAT}&lon={cls.LON}&appid={cls.API_KEY}&units=metric"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                temperature = data["main"]["temp"]
                return temperature > 28
        except requests.exceptions.RequestException:
            pass
        return False


_PRODUCT_DF = pd.DataFrame({
    "product_name": ["Chocolate", "Granizado", "Limon", "Dulce de Leche"],
    "quantity": [3, 10, 0, 5]
})

available_discount_codes = [
    "Primavera2021",
    "Verano2021",
    "Navidad2x1",
    "heladoFrozen"
]

available_discount_codes = {
    _PRODUCT_DF["product_name"][i]: available_discount_codes[i]
    for i in range(len(_PRODUCT_DF["product_name"]))
}

def is_product_available(product_name, quantity):
    product = _PRODUCT_DF[_PRODUCT_DF["product_name"].str.lower() == product_name.lower()]
    if not product.empty:
        available_quantity = product.iloc[0]["quantity"]
        return available_quantity >= quantity
    return False


def chat_index(request):
    return render(request, 'index.html')


@require_POST
@csrf_exempt
def handle_message(request):
    message = request.POST.get("message", "").lower()
    response = ""
    
    if GeoAPI.is_hot():
        response += "Bienvenido 1\n"
    else:
        response += "Bienvenido 2\n"

    print(f"Message received: {message}")


    if "hola" in message:
        response += "Hola, ¿en qué puedo ayudarte?"
        response += "solicitar pedido?"
    elif any(option in message for option in ["ok", "si", "solicitar pedido", "bueno"]):
        response = "Claro, ¿qué producto te gustaría pedir?" 
        response += str(_PRODUCT_DF)
    elif "hay stock" in message:
        response = "Nuestros productos y cantidades son los siguientes:\n"
        response += str(_PRODUCT_DF)
    elif any(product_name.lower() in message for product_name in _PRODUCT_DF["product_name"]):
        product_name = next((p for p in _PRODUCT_DF["product_name"] if p.lower() in message), None)
        if product_name:
            response = f"Tenemos {product_name}. Por favor, indícame la cantidad que deseas."
            request.session['product_name'] = product_name  # Almacenar el nombre del producto en la sesión
    elif 'product_name' in request.session and request.session['product_name'] and 'quantity' not in request.session:
        product_name = request.session['product_name']
        quantity_str = message.split()[0]  # Extraer la primera palabra del mensaje que debe ser la cantidad
        try:
            quantity = int(quantity_str)
            if quantity < 0:
                response = "La cantidad ingresada no es válida. Por favor, ingresa una cantidad mayor o igual a cero."
            elif quantity > _PRODUCT_DF.loc[_PRODUCT_DF['product_name'] == product_name, 'quantity'].values[0]:
                response = "La cantidad ingresada es superior al stock disponible. Por favor, elige una cantidad menor o igual al stock."
            else:
                response = "Cantidad válida. Ahora ingresa el cupón de descuento válido:"
                request.session['quantity'] = quantity  # Almacenar la cantidad en la sesión
        except ValueError:
            response = "La cantidad ingresada no es válida. Por favor, ingresa solo números para la cantidad."
    elif 'product_name' in request.session and 'quantity' in request.session and 'coupon' not in request.session:
        product_name = request.session['product_name']
        quantity = request.session['quantity']
        coupon = message

        print(f"Product name: {product_name}")
        print(f"Coupon: {coupon}")

        if product_name in available_discount_codes:
            if (
                coupon.lower() == available_discount_codes[product_name].lower()
                or (coupon.isdigit() and coupon.lower() == str(available_discount_codes[product_name])[:5].lower())
            ):
                response = "Cupón válido. Pedido confirmado."
                response += "Que Tenga Buen dia."
                del request.session['product_name']  # Eliminar el nombre del producto de la sesión
                del request.session['quantity']  # Eliminar la cantidad de la sesión
            else:
                response = "Cupón incorrecto. Por favor, ingresa un cupón válido."
        else:
            response = "No hay un cupón de descuento disponible para este producto."
    else:
        response = "Lo siento, no puedo entender tu mensaje."

    return HttpResponse(response or "")





