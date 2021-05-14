import mysql.connector
from mysql.connector.cursor import CursorBase

from pathgenerator.config import DB_HOST, DB_DATABASE, DB_USER, DB_PASSWORD, \
    BLOCKS_TABLE, USERS_TABLE, WORLDS_TABLE, POSITIONS_TABLE, OBSERVATIONS_TABLE, WORLDS


MAPS_IN_QUERY = '(' + (','.join(f"'{world}'" for world in WORLDS)) + ')'

class DataFetcher:
    """
    Used to fetch position, block, and observation data for a given user between two given times.
    Connects to the configured MySQL database for this information.
    """

    def __init__(self, host, database, user, password, username, start_time, end_time):
        creds = {
            'host': host,
            'database': database,
            'user': user,
            'password': password,
            'use_pure': True,
            'charset': 'utf8',
        }

        self._username = username
        self._start_time = start_time
        self._end_time = end_time

        mydb = mysql.connector.connect(**creds)
        self._cursor: CursorBase = mydb.cursor()

        # Fetch all the data
        self.position_data = self._fetch_position_data()
        self.block_data = self._fetch_block_data()
        self.observation_data = self._fetch_observation_data()

        self._cursor.close()

    def _fetch_position_data(self):
        """Fetch all position data ordered by time"""
        self._cursor.execute(
            "SELECT world AS world_name, x, y, z, time "
            f"FROM {POSITIONS_TABLE} "
            f"WHERE username = '{self._username}' "
            f"AND time BETWEEN {self._start_time} AND {self._end_time} "
            f"AND world IN {MAPS_IN_QUERY} "
            "ORDER BY time ASC"
        )
        return self._cursor.fetchall()

    def _fetch_block_data(self):
        """
        Fetches all block data.
        `action` corresponds to 0 if block was placed and 1 if block was broken.
        """
        self._cursor.execute(
            "SELECT ("
            f" SELECT world FROM {WORLDS_TABLE} WHERE id = wid) AS world_name, "
            " x, y, z, action "
            f"FROM {BLOCKS_TABLE} as b "
            f"WHERE time BETWEEN {self._start_time} AND {self._end_time} "
            f"AND user = (SELECT rowid FROM {USERS_TABLE} WHERE user = '{self._username}') "
            f"AND wid IN {MAPS_IN_QUERY} "
            "ORDER BY time ASC"
        )
        return self._cursor.fetchall()

    def _fetch_observation_data(self):
        """Fetches all observations"""
        self._cursor.execute(
            "SELECT world AS world_name, x, y, z, observation "
            f"FROM {OBSERVATIONS_TABLE} "
            f"WHERE username = '{self._username}' "
            f"AND time between {self._start_time * 1000} AND {self._end_time * 1000} "
            f"AND world IN {MAPS_IN_QUERY} "
        )
        return self._cursor.fetchall()
