from asynctest import TestCase, mock, CoroutineMock
from api.carbon import CarbonAPI
from api.api_connection import ApiConnection


class TestCarbonAPI(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.carbon = CarbonAPI()

    def setUp(self):
        pass

    def tearDown(self):
        pass

    async def test_current_national_intensity(self):
        data = {'data': [{'intensity': {'actual': 170, 'index': 'moderate'}}]}
        with mock.patch.object(ApiConnection, "get", return_value=data):
            result = await self.carbon.current_national_intensity()
            self.assertEqual(result, (170, 'moderate'))

    async def test_current_region_intensity(self):
        data = {'data': [{'data': [{'intensity': {'forecast': 170, 'index': 'moderate'}}]}]}
        with mock.patch.object(ApiConnection, "get", return_value=data):
            result = await self.carbon.current_region_intensity(3)
            self.assertEqual(result, (170, 'moderate'))

    async def test_current_national_mix(self):
        data = {'data': {'generationmix': [{"fuel": "biomass", "perc": 3.6}, {"fuel": "coal", "perc": 0.4}]}}
        with mock.patch.object(ApiConnection, "get", return_value=data):
            result = await self.carbon.current_national_mix()
            self.assertEqual(result, {'biomass': 3.6, 'coal': 0.4})

    async def test_current_region_mix(self):
        result = await self.carbon.current_region_mix()
        self.assertTrue(result)

    async def test_national_forecast(self):
        result = await self.carbon.national_forecast()
        self.assertTrue(result)

    async def test_region_forecast(self):
        result = await self.carbon.region_forecast()
        self.assertTrue(result)
