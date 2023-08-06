import random
import time
import requests
from typing import List, Union


class API:
	def __init__(
		self,
		api_key: str
	):
		self.api_key = api_key
		self._headers = {"API-KEY": self.api_key}
		self._session = requests.session()
		self._session.headers = self._headers

		# URL / Endpoints
		self._base_url = "https://api-testing.mozio.com/v2/"
		self._search_endpoint = "search/"
		self._reservation_endpoint = "reservations/"

	def do_search(
		self,
		**kwargs
	) -> str:
		"""
		:param kwargs: Search queries (payload)
		:return: search_id
		"""
		response = self._session.post(self._base_url + self._search_endpoint, json=kwargs)

		# Handles
		if not response.ok:
			...

		return response.json()['search_id']

	def search_poll(
		self,
		search_id: str
	) -> Union[None, List[dict]]:
		"""
		:param search_id:
		:return: None if more_coming else results
		"""
		response = self._session.get(f"{self._base_url}{self._search_endpoint}{search_id}/poll/")

		# Handles
		if not response.ok:
			...

		response_data = response.json()
		if not response_data['more_coming']:
			return response_data['results']

	def create_reservation(
		self,
		**kwargs
	) -> None:
		response = self._session.post(self._base_url + self._reservation_endpoint, json=kwargs)

		# Handles
		if not response.ok:
			...

	def reservations_poll(
		self,
		search_id
	) -> List[dict]:
		"""
		:param search_id: search id used in `do_search`
		:return: None if more_coming else reservations
		"""
		response = self._session.get(f"{self._base_url}{self._reservation_endpoint}{search_id}/poll/")

		# Handle
		if not response.ok:
			...

		response_data = response.json()
		if response_data['status'] != "pending":
			return response_data['reservations']

	def cancel_reservation(
		self,
		reservation_id: str
	) -> dict:
		"""
		:param reservation_id:
		:return: Response
		"""
		response = self._session.delete(f"{self._base_url}{self._reservation_endpoint}{reservation_id}")

		# Handle
		if not response.ok:
			...

		return response.json()


if __name__ == "__main__":
	API_KEY = "6bd1e15ab9e94bb190074b4209e6b6f9"
	api = API(API_KEY)

	# Test case data
	search_data = {
		"start_address": "44 Tehama Street, San Francisco, CA, USA",
		"end_address": "SFO",
		"mode": "one_way",
		"pickup_datetime": "2023-12-01 15:30",
		"num_passengers": 2,
		"currency": "USD",
		"campaign": "{your full name}"
	}
	search_id_result = api.do_search(**search_data)  # Does initial search with test data

	# Polls till results are complete
	while not (results := api.search_poll(search_id_result)):
		time.sleep(1)

	# Get minimum vehicle cost with "Dummy External Provider" provider name
	min_cost = float('inf')
	for result in results:
		steps = result['steps']
		for step in steps:
			details = step['details']
			if details['provider_name'] == "Dummy External Provider":
				provider_cost = float(details['price']['price']['value'])
				if provider_cost < min_cost:
					min_cost = provider_cost
					result_id = result['result_id']

	# Data used to make a reservation
	reservation_data = {
		"first_name": "Dummy First",
		"last_name": "Dummy Last",
		"email": "Dummy@email.com",
		"phone_number": "17575771111",
		"country_code_name": "US",
		"search_id": search_id_result,
		"result_id": result_id,
		"airline": "AA",
		"flight_number": random.randint(1, 1000)
	}

	# Create the reservation
	api.create_reservation(**reservation_data)

	# Poll the reservation
	while not (reservations := api.reservations_poll(search_id_result)):
		time.sleep(1)

	# Cancel reservation
	for reservation in reservations:  # In case of multiple
		print("Reservation ID: ", reservation['id'])
		api.cancel_reservation(reservation['id'])
