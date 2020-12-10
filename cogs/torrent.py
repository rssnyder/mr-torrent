import os
import discord
import requests
import json
import logging
from discord.ext import commands
from qbittorrent import Client

logging.basicConfig(level=logging.INFO)


def load_json(token):
    with open('./config.json') as f:
        config = json.load(f)
    return config.get(token)


def setup(client):
    client.add_cog(Torrent(client))


class Torrent(commands.Cog):

    def __init__(self, client):
        self.client = client

        qb = Client(load_json('qbt_url'))

        qb.login('admin', os.getenv('QBT_KEY'))

        self.qb = qb


    @commands.Cog.listener()
    async def on_ready(self):
        logging.info('torrent cog ready')
    

    @commands.command()
    async def torrent(self, ctx, *message: str):
        """
        General purpose torrent command
        Usage: !torrent <command> <args>
        """

        # Stop all downloading
        if message[0].lower() == 'stop':
            self.pause()

            await ctx.send('Torrents stopped')

        # Start all downloading
        elif message[0].lower() == 'start':
            self.resume()

            await ctx.send('Torrents started')

        # Search for a torrent via TPB
        elif message[0].lower() == 'search':
            search_string = '+'.join(message[1:])
            magnet_embed = self.get_magnet(search_string)
            
            await ctx.send(embed=magnet_embed)

        # Download a torrent via magnet link
        elif message[0].lower() == 'download':
            self.download(message[1])

        # Get info on downloading torrent
        elif message[0].lower() == 'info':
            found = self.find(message[1:])

            if not found:
                await ctx.send('No matching torrent found')
            else:
                await ctx.send(embed=found)
        
        # Get help to download torrent
        elif message[0].lower() == 'keys':
            await ctx.send(embed=discord.Embed(
                title=f'Navigate to {load_json("download_url")}',
                description=f'Key: discord\nSecret: {os.getenv("MINIO_KEY")}'
            ))
        
        # Get help
        elif message[0].lower() == 'help':
            help_text = 'Usage: !torrent <command> <args>\n'
            help_text += 'Find torrents to download: !torrent search <search string>\n'
            help_text += 'Queue torrents for download: !torrent download <magnet link>\n'
            help_text += 'Monitor download progress: !torrent info <search string>\n'
            help_text += 'How to download your torrent: !torrent keys'


            await ctx.send(embed=discord.Embed(
                title='Hello! My Name is Mr. Torrent',
                description=help_text
            ))
        
        else:
            await ctx.send('Invalid command')
        
        # await ctx.send(embed=magnet_embed)
    
    def get_magnet(self, search: str) -> discord.Embed:
        """
        Get a magnet link for a torrent.
        Use the backend api for thepiratebay website
        """

        failure = discord.Embed(
            title='Unable to find torrent',
            url=f'https://www.thepiratebay.org/search/{search}',
            description='No Magnet Found'
        )

        try:
            response = requests.get(f'https://apibay.org/q.php?q={search}')
        except requests.ConnectionError:
            logging.info('Unable to reach apibay.org!')
            return failure

        # Top torrent
        target = json.loads(response.content)[0]

        # No torrent found
        if target.get('id') == '0':
            return failure

        # Top torrent info
        desc = f"Magnet: magnet:?xt=urn:btih:{target.get('info_hash')}&dn={target.get('name')}\n\n"
        desc += f"Seeders: {target.get('seeders')}\nLeachers: {target.get('leechers')}\n"
        desc += f"Uploader: {target.get('username')}\n"
        desc += 'Size: {:.2}GB\n'.format(int(target.get('size')) / 1000000000)

        success = discord.Embed(
            title=target.get('name'),
            url=f'https://thepiratebay.org/description.php?id={target.get("id")}',
            description=desc
        )

        logging.info('<torrent> Found: ' + target.get('name'))
        return success


    def download(self, magnet_link: str) -> discord.Embed:
        """
        Download a magnet link.
        Use qbittorrent sdk
        """

        self.qb.download_from_link(magnet_link, savepath=load_json('download_path'))
        logging.info('<torrent> Downloaded: ' + magnet_link)


    def pause(self):
        """
        Pause all downloads
        """

        self.qb.pause_all()
        logging.info('<torrent> Paused')


    def resume(self):
        """
        Resume all downloads
        """

        self.qb.resume_all()
        logging.info('<torrent> Started')


    def find(self, name: str):
        """
        Get info on a torrent
        """

        # Get all current downloads
        torrents = self.qb.torrents()

        # Find matching torrent
        for torrent in torrents:
            if ' '.join(name).lower() in torrent['name'].lower():

                summary = 'Progress: {:.2%}\n'.format(torrent['progress'])
                summary += 'Ratio: {:.2}'.format(torrent['ratio'])

                # Nice
                if str(torrent['ratio'])[:2] == '69':
                    summary += ' **nice**'
                
                found = discord.Embed(
                    title=torrent['name'],
                    description=summary
                )

                logging.info('<torrent> Info: ' + torrent['name'])
                return found