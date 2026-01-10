"""
WeatherService - Fase 3: Clima com OpenWeather
Extrai condições climáticas de partidas futuras para análise de impacto.
"""

import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from django.conf import settings

logger = logging.getLogger(__name__)


class WeatherService:
    """
    Serviço de consulta de clima para estádios.
    Usa OpenWeather OneCall API 3.0 para previsões de até 7 dias.
    """
    
    def __init__(self):
        self.api_key = settings.OPENWEATHER_API_KEY
        self.base_url = settings.OPENWEATHER_API_URL
        self.timeout = 10
        
    def get_weather_for_match(
        self, 
        latitude: float, 
        longitude: float, 
        match_datetime: datetime
    ) -> Optional[Dict[str, Any]]:
        """
        Obtém condições climáticas previstas para o momento da partida.
        
        Args:
            latitude: Latitude do estádio
            longitude: Longitude do estádio
            match_datetime: Data/hora da partida
            
        Returns:
            Dict com clima previsto ou None se não disponível
        """
        try:
            # Validar se a partida está dentro da janela de previsão (7 dias)
            now = datetime.now()
            time_diff = match_datetime - now
            
            if time_diff.total_seconds() < 0:
                logger.warning(f"Partida já ocorreu: {match_datetime}")
                return None
                
            if time_diff.days > 7:
                logger.warning(f"Partida muito distante para previsão: {match_datetime} ({time_diff.days} dias)")
                return None
            
            # Chamar OneCall API 3.0
            url = f"{self.base_url}/forecast"
            params = {
                'lat': latitude,
                'lon': longitude,
                'appid': self.api_key,
                'units': 'metric',  # Celsius
                'cnt': 40  # 40 timestamps (5 dias a cada 3h)
            }
            
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            # Encontrar a previsão mais próxima do horário da partida
            closest_forecast = self._find_closest_forecast(data.get('list', []), match_datetime)
            
            if not closest_forecast:
                logger.warning(f"Nenhuma previsão encontrada para {match_datetime}")
                return None
            
            # Extrair dados relevantes
            weather_data = self._extract_weather_data(closest_forecast)
            
            logger.info(f"Clima obtido para partida: {weather_data.get('condition')} - {weather_data.get('temp')}°C")
            return weather_data
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout ao consultar OpenWeather para ({latitude}, {longitude})")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao consultar OpenWeather: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado no WeatherService: {str(e)}")
            return None
    
    def _find_closest_forecast(self, forecasts: list, target_datetime: datetime) -> Optional[Dict]:
        """
        Encontra a previsão mais próxima do horário da partida.
        """
        if not forecasts:
            return None
        
        closest = None
        min_diff = float('inf')
        
        for forecast in forecasts:
            forecast_time = datetime.fromtimestamp(forecast.get('dt', 0))
            time_diff = abs((forecast_time - target_datetime).total_seconds())
            
            if time_diff < min_diff:
                min_diff = time_diff
                closest = forecast
        
        return closest
    
    def _extract_weather_data(self, forecast: Dict) -> Dict[str, Any]:
        """
        Extrai dados relevantes da previsão.
        """
        main = forecast.get('main', {})
        weather = forecast.get('weather', [{}])[0]
        wind = forecast.get('wind', {})
        rain = forecast.get('rain', {})
        snow = forecast.get('snow', {})
        clouds = forecast.get('clouds', {})
        
        # Temperatura
        temp = main.get('temp', 20)
        feels_like = main.get('feels_like', temp)
        humidity = main.get('humidity', 50)
        
        # Condição principal
        condition = weather.get('main', 'Clear')
        description = weather.get('description', 'clear sky')
        
        # Vento (m/s)
        wind_speed = wind.get('speed', 0)
        
        # Precipitação (mm nas últimas 3h)
        rain_3h = rain.get('3h', 0) if rain else 0
        snow_3h = snow.get('3h', 0) if snow else 0
        precipitation = rain_3h + snow_3h
        
        # Nebulosidade (%)
        cloud_coverage = clouds.get('all', 0)
        
        # Classificar impacto no jogo
        impact = self._calculate_weather_impact(
            condition=condition,
            temp=temp,
            wind_speed=wind_speed,
            precipitation=precipitation
        )
        
        return {
            'temp': round(temp, 1),
            'feels_like': round(feels_like, 1),
            'humidity': humidity,
            'condition': condition,
            'description': description,
            'wind_speed': round(wind_speed, 1),
            'precipitation': round(precipitation, 1),
            'cloud_coverage': cloud_coverage,
            'impact': impact,
            'timestamp': forecast.get('dt')
        }
    
    def _calculate_weather_impact(
        self,
        condition: str,
        temp: float,
        wind_speed: float,
        precipitation: float
    ) -> str:
        """
        Calcula o impacto das condições climáticas no jogo.
        
        Returns:
            'high' | 'medium' | 'low'
        """
        impact_score = 0
        
        # Condição adversa
        adverse_conditions = ['Rain', 'Snow', 'Thunderstorm', 'Drizzle']
        if condition in adverse_conditions:
            impact_score += 3
        
        # Temperatura extrema
        if temp < 5 or temp > 35:
            impact_score += 2
        elif temp < 10 or temp > 30:
            impact_score += 1
        
        # Vento forte (> 10 m/s = ~36 km/h)
        if wind_speed > 15:
            impact_score += 3
        elif wind_speed > 10:
            impact_score += 2
        elif wind_speed > 7:
            impact_score += 1
        
        # Precipitação
        if precipitation > 10:
            impact_score += 3
        elif precipitation > 5:
            impact_score += 2
        elif precipitation > 1:
            impact_score += 1
        
        # Classificação final
        if impact_score >= 6:
            return 'high'
        elif impact_score >= 3:
            return 'medium'
        else:
            return 'low'
    
    def get_stadium_coordinates(self, venue_name: str, city: str) -> Optional[tuple]:
        """
        Obtém coordenadas de um estádio por nome/cidade.
        Usa Geocoding API do OpenWeather.
        
        Args:
            venue_name: Nome do estádio
            city: Cidade
            
        Returns:
            (latitude, longitude) ou None
        """
        try:
            url = f"http://api.openweathermap.org/geo/1.0/direct"
            params = {
                'q': f"{venue_name}, {city}",
                'limit': 1,
                'appid': self.api_key
            }
            
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                logger.warning(f"Coordenadas não encontradas para {venue_name}, {city}")
                return None
            
            location = data[0]
            latitude = location.get('lat')
            longitude = location.get('lon')
            
            if latitude and longitude:
                logger.info(f"Coordenadas obtidas: {venue_name} -> ({latitude}, {longitude})")
                return (latitude, longitude)
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao obter coordenadas: {str(e)}")
            return None


# Cache de coordenadas de estádios conhecidos (evita chamadas repetidas)
STADIUM_COORDINATES = {
    # Premier League
    'Old Trafford': (53.4631, -2.2913),
    'Anfield': (53.4308, -2.9608),
    'Emirates Stadium': (51.5549, -0.1084),
    'Stamford Bridge': (51.4816, -0.1909),
    'Etihad Stadium': (53.4831, -2.2004),
    'Tottenham Hotspur Stadium': (51.6042, -0.0664),
    
    # La Liga
    'Santiago Bernabéu': (40.4530, -3.6884),
    'Camp Nou': (41.3809, 2.1228),
    'Wanda Metropolitano': (40.4362, -3.5995),
    
    # Serie A
    'San Siro': (45.4780, 9.1240),
    'Allianz Stadium': (45.1096, 7.6410),
    'Stadio Olimpico': (41.9341, 12.4547),
    
    # Bundesliga
    'Allianz Arena': (48.2188, 11.6247),
    'Signal Iduna Park': (51.4925, 7.4517),
    
    # Ligue 1
    'Parc des Princes': (48.8414, 2.2530),
    
    # Moçambique
    'Estádio do Zimpeto': (-25.9950, 32.6556),
    'Estádio da Machava': (-25.9953, 32.5833),
}
