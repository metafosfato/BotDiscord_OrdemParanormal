import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional

from src.adapters.cris.cris_fetcher import CRISFetcherAdapter
from src.adapters.repository.memory_repository import MemoriaPersonagemRepository
from src.adapters.llm.gemini_adapter import GeminiLLMAdapter
from src.adapters.audio.edge_tts_adapter import EdgeTTSAdapter
from src.use_cases.importar_personagem import ImportarPersonagemCRISUseCase
from src.use_cases.executar_teste_mecanico import ExecutarTesteMecanicoUseCase
from src.use_cases.processar_interacao_mestre import ProcessarInteracaoMestreUseCase

class SessionCog(commands.Cog):
    """
    Cog principal de gerenciamento de sessões do RPG Ordem Paranormal no Discord.
    Suporta tanto comandos Slash (/) quanto Prefixo (!).
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.repository = MemoriaPersonagemRepository()
        self.cris_adapter = CRISFetcherAdapter()
        self.llm_service = GeminiLLMAdapter()
        self.audio_service = EdgeTTSAdapter()

        # Instância dos Casos de Uso
        self.importar_uc = ImportarPersonagemCRISUseCase(self.cris_adapter, self.repository)
        self.teste_mecanico_uc = ExecutarTesteMecanicoUseCase(self.repository)
        self.mestre_uc = ProcessarInteracaoMestreUseCase(
            llm_service=self.llm_service,
            audio_service=self.audio_service
        )

        # Mapeamento de id de usuário Discord -> id de personagem importado
        self.user_character_map = {}

    # --- MÉTODO DE SINCRONIZAÇÃO INSTANTÂNEA ---
    @commands.command(name="sync")
    @commands.has_permissions(administrator=True)
    async def sync_commands(self, ctx: commands.Context):
        """Força a sincronização instantânea dos comandos Slash no servidor atual."""
        try:
            synced = await self.bot.tree.sync(guild=ctx.guild)
            await ctx.send(f"✅ **{len(synced)}** comando(s) Slash sincronizados instantaneamente para este servidor!")
        except Exception as e:
            await ctx.send(f"❌ Erro ao sincronizar: {str(e)}")

    # --- COMANDOS: IMPORTAR FICHA ---
    async def _processar_importar_ficha(self, user: discord.User, url: str) -> discord.Embed:
        personagem = self.importar_uc.executar(url)
        self.user_character_map[str(user.id)] = personagem.id

        embed = discord.Embed(
            title=f"📁 Ficha Importada: {personagem.nome}",
            description=f"**Jogador:** {user.mention}\n**Origem:** {personagem.origem or 'Investigador'}",
            color=discord.Color.dark_purple()
        )
        embed.add_field(
            name="📊 Atributos",
            value=f"AGI: `{personagem.atributos['AGI']}` | FOR: `{personagem.atributos['FOR']}` | INT: `{personagem.atributos['INT']}` | PRE: `{personagem.atributos['PRE']}` | VIG: `{personagem.atributos['VIG']}`",
            inline=False
        )
        embed.add_field(
            name="❤️ Status",
            value=f"**PV:** `{personagem.vida_atual}/{personagem.vida_maxima}` | **SAN:** `{personagem.sanidade_atual}/{personagem.sanidade_maxima}` | **PE:** `{personagem.pe_atual}/{personagem.pe_maximo}`",
            inline=False
        )
        embed.set_footer(text="Ordem Paranormal Bot • Domínio Determinístico")
        return embed

    @app_commands.command(name="importar_ficha", description="Importa a ficha de personagem pública do C.R.I.S. pelo link.")
    @app_commands.describe(url="Link público da ficha no CRIS (ex: https://crisordemparanormal.com/ficha/...)")
    async def importar_ficha_slash(self, interaction: discord.Interaction, url: str):
        await interaction.response.defer(thinking=True)
        try:
            embed = await self._processar_importar_ficha(interaction.user, url)
            await interaction.followup.send(embed=embed)
        except Exception as e:
            await interaction.followup.send(f"❌ Erro ao importar ficha do C.R.I.S.: {str(e)}")

    @commands.command(name="importar_ficha")
    async def importar_ficha_prefix(self, ctx: commands.Context, url: str):
        try:
            embed = await self._processar_importar_ficha(ctx.author, url)
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Erro ao importar ficha do C.R.I.S.: {str(e)}")

    # --- COMANDOS: ROLAR TESTE ---
    async def _processar_rolar(self, user: discord.User, pericia: str, dt: Optional[int] = None):
        user_id = str(user.id)
        char_id = self.user_character_map.get(user_id)

        if not char_id:
            return None, "⚠️ Você ainda não importou um personagem! Use `/importar_ficha <url>` ou `!importar_ficha <url>` primeiro."

        resultado = self.teste_mecanico_uc.executar(char_id, pericia, dt=dt)
        cor = discord.Color.green() if resultado.sucesso is True else (discord.Color.red() if resultado.sucesso is False else discord.Color.gold())

        embed = discord.Embed(
            title=f"🎲 Teste de {resultado.nome_pericia} ({resultado.nome_atributo})",
            color=cor
        )
        dados_str = ", ".join([f"`{d}`" for d in resultado.dados_rolados])
        embed.add_field(name="Dados Rolados (Nd20)", value=f"[{dados_str}]", inline=True)
        embed.add_field(name="Dado Escolhido", value=f"`{resultado.dado_escolhido}`", inline=True)
        embed.add_field(name="Bônus Perícia", value=f"`+{resultado.bonificacao}`", inline=True)
        embed.add_field(name="Total Final", value=f"**`{resultado.valor_total}`**", inline=False)

        if dt is not None:
            status_txt = "✅ **SUCESSO**" if resultado.sucesso else "❌ **FRACASSO**"
            embed.add_field(name=f"Resultado vs DT {dt}", value=status_txt, inline=False)

        if resultado.foi_critico:
            embed.add_field(name="🔥 CRÍTICO!", value="Margem de Ameaça atingida!", inline=False)
        elif resultado.foi_desastre:
            embed.add_field(name="💀 DESASTRE!", value="Rolagem de desastre crítico!", inline=False)

        return embed, None

    @app_commands.command(name="rolar", description="Executa um teste mecânico determinístico de perícia segundo as regras do sistema.")
    @app_commands.describe(pericia="Nome da perícia", dt="Dificuldade do Teste (DT) opcional")
    async def rolar_slash(self, interaction: discord.Interaction, pericia: str, dt: Optional[int] = None):
        embed, err = await self._processar_rolar(interaction.user, pericia, dt)
        if err:
            await interaction.response.send_message(err, ephemeral=True)
        else:
            await interaction.response.send_message(embed=embed)

    @commands.command(name="rolar")
    async def rolar_prefix(self, ctx: commands.Context, pericia: str, dt: Optional[int] = None):
        embed, err = await self._processar_rolar(ctx.author, pericia, dt)
        if err:
            await ctx.send(err)
        else:
            await ctx.send(embed=embed)

    # --- COMANDOS: FALAR MESTRE ---
    @app_commands.command(name="falar_mestre", description="Envia uma ação ao Mestre IA (Gemini) para narração da cena.")
    @app_commands.describe(acao="O que o seu personagem faz ou fala na cena.")
    async def falar_mestre_slash(self, interaction: discord.Interaction, acao: str):
        await interaction.response.defer(thinking=True)
        try:
            resposta = await self.mestre_uc.executar(interaction.user.display_name, acao)
            embed = discord.Embed(title="📜 Mestre da Ordem", description=resposta["texto_narracao"], color=discord.Color.dark_red())
            await interaction.followup.send(embed=embed)
        except Exception as e:
            await interaction.followup.send(f"❌ Erro na narração do Mestre: {str(e)}")

    @commands.command(name="falar_mestre")
    async def falar_mestre_prefix(self, ctx: commands.Context, *, acao: str):
        try:
            resposta = await self.mestre_uc.executar(ctx.author.display_name, acao)
            embed = discord.Embed(title="📜 Mestre da Ordem", description=resposta["texto_narracao"], color=discord.Color.dark_red())
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Erro na narração do Mestre: {str(e)}")

    # --- COMANDOS: STATUS SESSÃO ---
    @app_commands.command(name="status_sessao", description="Lista o status atual de todos os agentes na sessão.")
    async def status_sessao_slash(self, interaction: discord.Interaction):
        embed = self._gerar_embed_status()
        if not embed:
            await interaction.response.send_message("Nenhum agente ativo na sessão.", ephemeral=True)
        else:
            await interaction.response.send_message(embed=embed)

    @commands.command(name="status_sessao")
    async def status_sessao_prefix(self, ctx: commands.Context):
        embed = self._gerar_embed_status()
        if not embed:
            await ctx.send("Nenhum agente ativo na sessão.")
        else:
            await ctx.send(embed=embed)

    def _gerar_embed_status(self) -> Optional[discord.Embed]:
        personagens = self.repository.listar_todos()
        if not personagens:
            return None
        embed = discord.Embed(title="🛡️ Agentes da Ordem Ativos", color=discord.Color.blue())
        for p in personagens:
            condicoes_txt = f" | Condições: {', '.join(p.condicoes)}" if p.condicoes else ""
            embed.add_field(
                name=f"{p.nome} (Jogador: {p.jogador or 'Anônimo'})",
                value=f"PV: `{p.vida_atual}/{p.vida_maxima}` | SAN: `{p.sanidade_atual}/{p.sanidade_maxima}` | PE: `{p.pe_atual}/{p.pe_maximo}`{condicoes_txt}",
                inline=False
            )
        return embed

async def setup(bot: commands.Bot):
    await bot.add_cog(SessionCog(bot))
