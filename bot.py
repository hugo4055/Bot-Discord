import os
import logging
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer

import discord
from discord import app_commands
from discord.ext import commands

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("voidbot")

TOKEN = os.getenv("DISCORD_TOKEN", "").strip()
GUILD_ID = os.getenv("GUILD_ID", "").strip()
WELCOME_CHANNEL_ID = os.getenv("WELCOME_CHANNEL_ID", "").strip()
PORT = int(os.getenv("PORT", "10000"))

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path not in ("/", "/health"):
            self.send_response(404)
            self.end_headers()
            return
        body = b"VoidBot Discord is running."
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_args):
        pass

def start_health_server():
    server = HTTPServer(("0.0.0.0", PORT), HealthHandler)
    Thread(target=server.serve_forever, daemon=True).start()
    log.info("Health endpoint listening on port %s", PORT)

intents = discord.Intents.default()
intents.members = True

class VoidBot(commands.Bot):
    async def setup_hook(self):
        if GUILD_ID.isdigit():
            guild = discord.Object(id=int(GUILD_ID))
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            log.info("Synced commands to test server %s", GUILD_ID)
        else:
            await self.tree.sync()
            log.info("Synced global application commands")

bot = VoidBot(command_prefix="!", intents=intents, help_command=None)

@bot.event
async def on_ready():
    log.info("Logged in as %s (ID: %s)", bot.user, bot.user.id)
    await bot.change_presence(activity=discord.Game(name="/ajuda"))

@bot.tree.command(name="ajuda", description="Mostra os comandos do VoidBot.")
async def ajuda(interaction: discord.Interaction):
    embed = discord.Embed(title="🤖 VoidBot — Ajuda", description="Comandos disponíveis:", color=discord.Color.blurple())
    embed.add_field(name="/ping", value="Verifica a latência.", inline=False)
    embed.add_field(name="/userinfo", value="Informações de um membro.", inline=False)
    embed.add_field(name="/serverinfo", value="Informações do servidor.", inline=False)
    embed.add_field(name="/say", value="Envia uma mensagem (requer Gerenciar mensagens).", inline=False)
    embed.add_field(name="/limpar", value="Apaga de 1 a 100 mensagens (requer Gerenciar mensagens).", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="ping", description="Mostra a latência do bot.")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"🏓 Pong! {round(bot.latency * 1000)} ms")

@bot.tree.command(name="userinfo", description="Mostra informações de um membro.")
@app_commands.describe(membro="Membro que você quer consultar (opcional)")
async def userinfo(interaction: discord.Interaction, membro: discord.Member | None = None):
    membro = membro or interaction.user
    embed = discord.Embed(title=f"Informações de {membro}", color=discord.Color.blurple())
    embed.set_thumbnail(url=membro.display_avatar.url)
    embed.add_field(name="Nome", value=membro.mention, inline=True)
    embed.add_field(name="ID", value=str(membro.id), inline=True)
    embed.add_field(name="Conta criada", value=discord.utils.format_dt(membro.created_at, style="D"), inline=False)
    if membro.joined_at:
        embed.add_field(name="Entrou no servidor", value=discord.utils.format_dt(membro.joined_at, style="D"), inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="serverinfo", description="Mostra informações deste servidor.")
async def serverinfo(interaction: discord.Interaction):
    guild = interaction.guild
    if guild is None:
        await interaction.response.send_message("Use este comando dentro de um servidor.", ephemeral=True)
        return
    embed = discord.Embed(title=f"📊 {guild.name}", color=discord.Color.green())
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    embed.add_field(name="ID", value=str(guild.id), inline=True)
    embed.add_field(name="Membros", value=str(guild.member_count or "Desconhecido"), inline=True)
    embed.add_field(name="Criado em", value=discord.utils.format_dt(guild.created_at, style="D"), inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="say", description="Envia uma mensagem como o bot.")
@app_commands.default_permissions(manage_messages=True)
@app_commands.describe(mensagem="Mensagem para enviar")
async def say(interaction: discord.Interaction, mensagem: str):
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("Você precisa da permissão Gerenciar mensagens.", ephemeral=True)
        return
    await interaction.response.send_message("Mensagem enviada.", ephemeral=True)
    if interaction.channel:
        await interaction.channel.send(mensagem)

@bot.tree.command(name="limpar", description="Apaga de 1 a 100 mensagens.")
@app_commands.default_permissions(manage_messages=True)
@app_commands.describe(quantidade="Quantidade de mensagens para apagar (1 a 100)")
async def limpar(interaction: discord.Interaction, quantidade: app_commands.Range[int, 1, 100]):
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("Você precisa da permissão Gerenciar mensagens.", ephemeral=True)
        return
    if not isinstance(interaction.channel, (discord.TextChannel, discord.Thread)):
        await interaction.response.send_message("Use este comando em um canal de texto.", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    try:
        apagadas = await interaction.channel.purge(limit=quantidade)
        await interaction.followup.send(f"🧹 Apaguei {len(apagadas)} mensagens.", ephemeral=True)
    except discord.Forbidden:
        await interaction.followup.send("Não tenho permissão para apagar mensagens neste canal.", ephemeral=True)

@bot.event
async def on_member_join(member: discord.Member):
    if not WELCOME_CHANNEL_ID.isdigit():
        return
    channel = member.guild.get_channel(int(WELCOME_CHANNEL_ID))
    if channel is not None:
        try:
            await channel.send(f"👋 Bem-vindo(a), {member.mention}! Leia as regras e divirta-se.")
        except discord.Forbidden:
            log.warning("No permission to send welcome message.")

if __name__ == "__main__":
    if not TOKEN:
        raise SystemExit("Missing DISCORD_TOKEN environment variable.")
    start_health_server()
    bot.run(TOKEN, log_handler=None)
