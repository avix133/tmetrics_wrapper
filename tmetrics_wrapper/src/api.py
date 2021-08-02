import datetime
import logging

import requests

LOG = logging.getLogger(__name__)


class TMetricsAPI(object):
    def __init__(self, account_id: int, token: str, host: str):
        self._account_id = account_id
        self._host = host

        self._headers = {"Accept": 'application/json', "Authorization": f'Bearer {token}'}

    def get_time_entries(self, start_date: datetime.datetime, end_date: datetime.datetime) -> {}:
        params = {'startDate': start_date.isoformat(), 'endDate': end_date.isoformat()}
        LOG.debug(f'Getting time entries for params {params}')
        return self._request_get(url=f'{self._host}/api/v3/accounts/{self._account_id}/timeentries', params=params)

    def get_projects(self) -> {}:
        LOG.debug(f'Getting projects')
        return self._request_get(url=f'{self._host}/api/v3/accounts/{self._account_id}/timeentries/projects')

    def add_time_entry(self, project_id: int, note: str, start_time: datetime.datetime, end_time: datetime.datetime):
        data = {
            "project": {"id": project_id},
            "note": note,
            "startTime": start_time.isoformat(),
            "endTime": end_time.isoformat()
        }
        LOG.debug(f'Adding time entry with data: {data}')
        self._request_post(url=f'{self._host}/api/v3/accounts/{self._account_id}/timeentries', data=data)

    def _request_get(self, url: str, params: {} = None) -> {}:
        LOG.debug(f'Sending GET request for url: {url} with params {params}')
        if not params:
            params = {}
        try:
            response = requests.get(url, params=params, headers=self._headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            LOG.exception(e)
            raise SystemExit(e)

        LOG.debug(f'GET request returned {response}')
        return response.json()

    def _request_post(self, url: str, data: {}) -> {}:
        LOG.debug(f'Sending POST request for url: {url} with data {data}')
        try:
            response = requests.post(url, json=data, headers=self._headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            LOG.exception(e)
            raise SystemExit(e)

        LOG.debug(f'POST request returned {response}')

        return response.json()
