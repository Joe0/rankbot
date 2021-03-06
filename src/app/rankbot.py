from discord.ext import commands
import hashids

from app.utils import database
from app.utils import embed

class RankBot(commands.Bot):
    def setup_config(self, config):
        self._config = config
        self.db = database.RankDB(config["mongodb_host"], config["mongodb_port"])
        self.hasher = hashids.Hashids(salt="cEDH league")

    async def on_guild_join(self, guild):
        emsg = embed.msg(description=(
            "Please create a role and assign that role as the league "
            + "admin using `set_admin [role name]`"
        ))
        await guild.owner.send(embed=emsg)
        self.db.setup_indices(guild)
