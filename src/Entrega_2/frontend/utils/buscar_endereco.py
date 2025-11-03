from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

def buscar_cidade_bairro(endereco: str):
    """Retorna cidade e bairro a partir de um endereço usando Geopy + Nominatim."""
    try:
        geolocator = Nominatim(user_agent="meu_app_geopy")
        local = geolocator.geocode(endereco, timeout=10)

        if not local:
            return {"erro": "Endereço não encontrado"}

        dados = local.raw.get("address", {})
        cidade = (
            dados.get("city")
            or dados.get("town")
            or dados.get("municipality")
            or dados.get("village")
        )
        bairro = (
            dados.get("suburb")
            or dados.get("neighbourhood")
            or dados.get("city_district")
        )

        return {"cidade": cidade, "bairro": bairro}

    except (GeocoderTimedOut, GeocoderServiceError):
        return {"erro": "Serviço temporariamente indisponível"}

