from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily, REGISTRY
from api.carbon import CarbonAPI
import asyncio
import time
from datetime import datetime

LONDON = 13
NW_ENGLAND = 3


class Prometheus:
    def __init__(self):
        self.gauges = {
            'intensity': GaugeMetricFamily('intensity',
                                           'Carbon Intensity',
                                           labels=["timestamp", "location"]),
            'fuel_mix': GaugeMetricFamily('fuel_mix',
                                          'Current Fuel Mix',
                                          labels=["timestamp", "location", "fuel_type"]),
            'forecast': GaugeMetricFamily('intensity_forecast',
                                          'Current Fuel Mix',
                                          labels=["timestamp", "location", "time"])
        }
        self.api = CarbonAPI()

    def execute_synchronously(self, func):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        t = loop.create_task(func)
        r = loop.run_until_complete(t)
        return r

    def collect(self):
        api_calls = {
            "lon_int": self.api.current_region_intensity(LONDON),
            "man_int": self.api.current_region_intensity(NW_ENGLAND),
            "lon_mix": self.api.current_region_mix(LONDON),
            "man_mix": self.api.current_region_mix(NW_ENGLAND),
            "lon_forecast": self.api.region_forecast_range(LONDON, 12),
            "man_forecast": self.api.region_forecast_range(NW_ENGLAND, 12)
        }

        results = {}
        for metric, func in api_calls.items():
            # prometheus doesn't support an async collect function, so run api calls syncronously
            results[metric] = self.execute_synchronously(func)

        timestamp = str(datetime.now().timestamp())

        self.gauges['intensity'].add_metric(labels=[timestamp, "london"], value=results['lon_int'][0])
        self.gauges['intensity'].add_metric(labels=[timestamp, "manchester"], value=results['man_int'][0])

        for fuel, percent in results['lon_mix'].items():
            self.gauges['fuel_mix'].add_metric(labels=[timestamp, "london", fuel], value=percent)
        for fuel, percent in results['man_mix'].items():
            self.gauges['fuel_mix'].add_metric(labels=[timestamp, "manchester", fuel], value=percent)

        for forecast in results['lon_forecast']:
            self.gauges['forecast'].add_metric(labels=[timestamp, "london",
                                               forecast['time']],
                                               value=forecast['forecast'])
        for forecast in results['man_forecast']:
            self.gauges['forecast'].add_metric(labels=[timestamp, "manchester",
                                               forecast['time']],
                                               value=forecast['forecast'])

        for name, gauge in self.gauges.items():
            yield gauge


def main():
    REGISTRY.register(Prometheus())
    while True:
        time.sleep(10)


if __name__ == '__main__':
    start_http_server(8000)
    main()