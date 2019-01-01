import time
import psycopg2


class WaifuManager:

    def __init__(self):
        self.conn = None
        self.cur = None
        self.player_waifu = {}
        self.players = None
        self.waifus = None

    def connect(self, conn):
        self.conn = conn
        self.cur = self.conn.cursor()
        self.load_player_waifu()
    
    def add_waifu_to_player(self, mal_id, name, discord_id):
        mal_id = str(mal_id)
        discord_id = str(discord_id)
        if self.player_waifu.get(discord_id, None) is None:
            self.player_waifu[discord_id] = []
        self.waifus.add_waifu(mal_id, name)
        waifu_id = self.waifus.get_latest_waifu_id(mal_id)
        player_id = self.players.get_player_id(discord_id)
        self.player_waifu[discord_id].append(waifu_id)
        self.cur.execute("INSERT INTO player_waifu (player_id, waifu_id) VALUES (%s, %s)", (player_id, waifu_id))
        self.save()
    
    def load_player_waifu(self):
        self.cur.execute("SELECT player_id, waifu_id FROM player_waifu;")
        query = self.cur.fetchall()
        for row in query:
            player_id, waifu_id = row
            discord_id = self.players.get_player_by_id(player_id)
            if self.player_waifu.get(discord_id, None) is None:
                self.player_waifu[discord_id] = []
            self.player_waifu[discord_id].append(waifu_id)

    def save(self):
        self.conn.commit()


waifu_manager = WaifuManager()