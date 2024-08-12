import discord
from discord.ext import commands
from discord import app_commands

import slack_sdk
import os
from datetime import datetime
import pytz
import matplotlib.pyplot as plt
import japanize_matplotlib
from dotenv import load_dotenv



from utils.database import execute_query, fetch_data

japan = pytz.timezone('Asia/Tokyo')

load_dotenv()
review_channel = int(os.environ.get("REVIEW_CHANNEL"))

class DiscordBot(commands.Cog):
    def __init__(self, discord_token, slack_token, slack_channel):
        # 初期化
        self.discord_token = discord_token
        self.slack_token = slack_token
        self.slack_channel = slack_channel

        self.intents = discord.Intents.default()
        self.intents.message_content = True  # メッセージ内容を取得するためのインテント
        self.intents.guilds = True           # ギルド情報を取得するためのインテント
        self.intents.members = True          # メンバー情報を取得するためのインテント
        
        # Discordボットの設定
        self.bot = commands.Bot(command_prefix='/', intents=self.intents)
        # スラッククライアントの設定
        self.slack_client = slack_sdk.WebClient(token=slack_token)

        # イベントハンドラの設定
        @self.bot.event
        async def on_ready():
            print(f'Registered commands: {self.bot.commands}')
            print(f'Logged in as {self.bot.user}')
            for guild in self.bot.guilds:
                print(f'Connected to guild: {guild.name} (ID: {guild.id})')
            if guild:
                members = guild.members
                for member in members:
                    execute_query("""
                        INSERT INTO userdata (discord_id, username, discriminator) 
                        VALUES (%s, %s, %s) 
                        ON CONFLICT (discord_id) DO UPDATE 
                        SET username = EXCLUDED.username, 
                        discriminator = EXCLUDED.discriminator;
                    """, (member.id, member.name, member.discriminator))
                for channel in guild.channels:
                    execute_query("""
                        INSERT INTO channel (discord_channel_id, channel_name)
                        VALUES (%s, %s)
                        ON CONFLICT (discord_channel_id) DO NOTHING;
                    """, (channel.id, channel.name))
            await self.bot.tree.sync()
        
        @self.bot.event
        async def on_voice_state_update(member, before, after):
            now = datetime.now(japan)
            user_id = member.id
            room_id = after.channel.id if after.channel else None
            time = now.strftime("%Y年%m月%d日 %H:%M:%S")
            if before.channel is None and after.channel is not None:
                msg = f"{time}{member.nick}が{after.channel.name}に参加しました"
                execute_query("""
                    INSERT INTO review (user_id, room_id, start_time, end_time) 
                    VALUES (%s, %s, %s, NULL);
                """, (user_id, room_id, now))
                
            elif before.channel is not None and after.channel is None:
                msg = f"{time}{member.nick}が{before.channel.name}から退出しました"
                execute_query("""
                    UPDATE review 
                    SET end_time = %s 
                    WHERE user_id = %s AND end_time IS NULL;
                """, (now, user_id))
            await self.send_msg_to_slack(msg, slack_channel)


        # `/review {member_name}` コマンドの追加
        @self.bot.tree.command(name='review', description="指定されたメンバーの通話時間を表示します")
        async def review(interaction: discord.Interaction, member_name: str):
            if interaction.channel.id != review_channel:
                await interaction.response.send_message("このコマンドはこのチャンネルでは使用できません。")
                return
            if interaction.user.name == member_name:
                member = discord.utils.find(lambda m: m.name == member_name, interaction.guild.members)
                if member:
                    records = fetch_data("""
                        SELECT userdata.username, channel.channel_name, SUM(review.duration) AS total_duration 
                        FROM review
                        JOIN userdata ON review.user_id = userdata.discord_id 
                        JOIN channel ON review.room_id = channel.discord_channel_id 
                        WHERE userdata.username = %s 
                        AND review.start_time >= NOW() - INTERVAL '1 month' 
                        GROUP BY userdata.username, channel.channel_name;
                    """, (str(member),))
                    if records:
                        response_message = []
                        for record in records:
                            total_duration = record['total_duration']
                            total_seconds = total_duration.total_seconds()
                            hours = total_seconds / 3600
                            response_message.append(f"ユーザー: {record['username']}, チャンネル: {record['channel_name']}, 合計時間: {hours:.2f}時間")
                        formatted_message = "\n".join(response_message)
                        await interaction.response.send_message(formatted_message)
                    else:
                        await interaction.response.send_message("指定されたユーザーのデータが見つかりません。")
                else:
                    await interaction.response.send_message("メンバー名が間違っています")
            else:
                await interaction.response.send_message("あなたは指定されたメンバーではありません。")


        # `/graph {channel_name}` コマンドの追加
        @self.bot.tree.command(name='graph', description="指定されたチャンネルの通話時間ランキングを表示します")
        async def graph(interaction: discord.Interaction, channel_name: str):
            if interaction.channel.id != review_channel:
                await interaction.response.send_message("このコマンドはこのチャンネルでは使用できません。")
                return
            records = fetch_data("""
                SELECT userdata.username, SUM(review.duration) AS total_duration 
                FROM review
                JOIN userdata ON review.user_id = userdata.discord_id 
                JOIN channel ON review.room_id = channel.discord_channel_id 
                WHERE channel.channel_name = %s
                  AND review.start_time >= NOW() - INTERVAL '1 month'
                GROUP BY userdata.username 
                ORDER BY total_duration DESC 
                LIMIT 10;
            """, (channel_name,))
            if not records:
                await interaction.response.send_message("指定されたチャンネル名に関連するデータはありません。")
                return

            usernames = [record['username'] for record in records]
            total_duration = [round(record['total_duration'].total_seconds() /60, 2) for record in records]
            plt.figure(figsize=(10, 6))
            plt.bar(usernames, total_duration, color='skyblue')
            plt.xlabel('ユーザー名')
            plt.ylabel('総時間 (時間)')
            plt.title(f"{channel_name} チャンネルの総時間 (上位10名)")
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            # グラフを保存してから送信
            plt.savefig('graph.png')
            plt.close()
            
            # Discordに画像をアップロード
            await interaction.response.send_message(file=discord.File('graph.png'))


    async def send_msg_to_slack(self, message, channel):
        response = self.slack_client.chat_postMessage(channel=channel, text=message)
        return response

    def run_discord_bot(self):
        # ボットを起動する
        self.bot.run(self.discord_token)


