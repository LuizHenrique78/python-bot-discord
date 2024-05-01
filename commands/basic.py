import time
from typing import Union, Any

import discord
from discord.ext import commands
from git_gub import GithubIntegration, PrNotFond, RepositoryNotFound, BranchNotFound, DeployNotFound

import random


def _generate_random_color() -> int:
    # Gerar valores aleatórios para os componentes R, G e B
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)

    # Combinar os valores em um número inteiro
    color_int = (r << 16) + (g << 8) + b

    return color_int


def _create_not_found_embed_error(repo_name, error: Union[str, None]):
    embed = discord.Embed(
        title=error,
        description=f"{repo_name}",
        color=_generate_random_color())
    return embed


async def _create_pr_embed(pulls: Any, repo_name: str, ctx: Any):
    for pr in pulls:
        embed = discord.Embed(
            title=f'Pull Request #{pr.number} em {repo_name}',
            description=pr.title,
            color=_generate_random_color()
        )
        embed.set_author(name=pr.user.login, icon_url=pr.user.avatar_url)
        embed.add_field(name='Autor', value=pr.user.login, inline=True)
        embed.add_field(name='URL', value=pr.html_url, inline=False)
        embed.add_field(name='Labels',
                        value=', '.join(label.name for label in pr.labels) if pr.labels else 'Nenhum', inline=False)

        embed.set_footer(
            text=f'Criado em {pr.created_at.strftime("%d/%m/%Y %H:%M:%S")} | Última atualização em {pr.updated_at.strftime("%d/%m/%Y %H:%M:%S")}')

        await ctx.send(embed=embed)


async def _create_workflow_embed(repo_name: str, latest_run: Any, ctx: Any):
    if latest_run:
        embed = discord.Embed(
            title=f"Informações sobre a execução mais recente do workflow em {repo_name}",
            color=0x34c2eb
        )
        embed.add_field(name="ID", value=latest_run.id, inline=False)
        embed.add_field(name="Nome do workflow", value=latest_run.name, inline=False)
        embed.add_field(name="Status", value=latest_run.status, inline=False)
        embed.add_field(name="Conclusão", value=latest_run.conclusion, inline=False)
        embed.add_field(name="Data de criação", value=latest_run.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
        embed.add_field(name="Data de conclusão", value=latest_run.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
                        inline=False)

        # Adiciona o nome da pull request, se disponível
        if latest_run.pull_requests:
            pr_name = latest_run.pull_requests[0].title
            embed.add_field(name="Pull Request", value=pr_name, inline=False)

        # Adiciona a URL do deploy
        deploy_url = latest_run.html_url
        embed.add_field(name="URL do Deploy", value=deploy_url, inline=False)

        # Adiciona um rodapé com uma mensagem informativa
        embed.set_footer(text="Para mais informações, consulte o GitHub.")

        # Adiciona uma imagem ao embed (opcional)
        embed.set_thumbnail(url="https://i.imgur.com/PMzk8ST.png")

        await ctx.send(embed=embed)
    else:
        await ctx.send(embed=_create_not_found_embed_error(repo_name, "Deploy Not Found"))


class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def clear(self, ctx, quantity=1):
        if ctx.message.author.guild_permissions.manage_messages:
            await ctx.channel.purge(limit=quantity + 1)
            await ctx.send(f'{quantity} mensagens foram limpas por {ctx.message.author.mention}.')
        else:
            await ctx.send("Você não tem permissão para executar esse comando.")

    @commands.command()
    async def ping(self, ctx):
        start_time = time.time()
        message = await ctx.send("Pong!")
        end_time = time.time()
        latency = (end_time - start_time) * 1000
        await message.edit(content=f"Pong! Latência do bot: {latency:.2f}ms")

    @commands.command()
    async def last_deploy(self, ctx, repo_name: str):
        try:
            workflow = GithubIntegration().get_latest_workflow_run(repo_name)

        except DeployNotFound as e:
            embed = _create_not_found_embed_error(repo_name, e.msg)
            await ctx.send(embed=embed)
            return

        await _create_workflow_embed(repo_name, workflow, ctx)

    @commands.command()
    async def prs(self, ctx, repo_name: str):
        try:
            pulls = GithubIntegration().get_pull_requests(repo_name)
        except RepositoryNotFound as e:
            embed = _create_not_found_embed_error(repo_name, e.msg)
            await ctx.send(embed=embed)
            return

        except PrNotFond as e:
            embed = _create_not_found_embed_error(repo_name, e.msg)
            await ctx.send(embed=embed)
            return

        except BranchNotFound as e:
            embed = _create_not_found_embed_error(repo_name, e.msg)
            await ctx.send(embed=embed)
            return

        await _create_pr_embed(pulls, repo_name, ctx)

    @commands.Cog.listener()
    async def on_github_webhook(self, request):
        payload = await request.json()
        if 'action' in payload and 'repository' in payload:
            action = payload['action']
            repository = payload['repository']['full_name']
            await self.send_message(f"Evento do GitHub: Ação '{action}' em '{repository}'")

        return web.Response(status=200, text="OK")


def setup(bot):
    return bot.add_cog(Basic(bot))
