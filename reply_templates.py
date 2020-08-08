_poolinfo_reply_EN = """
<b><code>{ticker}</code> {pool_name}</b>
<i>{desc}</i>
🌐{homepage}

<b>ℹ️ Pool info</b>
    rank: <code>#️{pool_rank}</code>
    pledge: <code>{pledge_ada} ₳</code>
    cost: <code>{cost_ada} ₳</code>
    margin: <code>{margin_perc}%</code>

<b>📈 Metrics</b>
    saturation: <code>{saturat}</code>
    controlled stake: <code>{rel_stake_perc}%</code>
    produced blocks: <code>{blocks}</code>
    rewards: <code>{rewards_ada} ₳</code>
"""

_poolinfo_reply_PT = """
<b><code>{ticker}</code> {pool_name}</b>
<i>{desc}</i>
🌐{homepage}

<b>ℹ️ Informações da pool</b>
    rank: <code>#️{pool_rank}</code>
    pledge: <code>{pledge_ada} ₳</code>
    custo: <code>{cost_ada} ₳</code>
    margem: <code>{margin_perc}%</code>

<b>📈 Métricas</b>
    saturação: <code>{saturat}</code>
    stake controlado: <code>{rel_stake_perc}%</code>
    blocos produzidos: <code>{blocks}</code>
    recompensas: <code>{rewards_ada} ₳</code>
"""

poolinfo_reply = {
    'EN': _poolinfo_reply_EN,
    'PT': _poolinfo_reply_PT}

###############################################################################

_poolinfo_reply_error_EN = """
Sorry, I didn't find the <code>{ticker}</code> pool 😞
"""

_poolinfo_reply_error_PT = """
Desculpa, não achei a pool <code>{ticker}</code> 😞
"""

poolinfo_reply_error = {
    'EN': _poolinfo_reply_error_EN,
    'PT': _poolinfo_reply_error_PT}

###############################################################################

_poolinfo_reply_wait_EN = """
I'm searching for the pool, one moment please... ⌛
"""

_poolinfo_reply_wait_PT = """
Estou procurando a pool, um momento por favor... ⌛
"""

poolinfo_reply_wait = {
    'EN': _poolinfo_reply_wait_EN,
    'PT': _poolinfo_reply_wait_PT}

###############################################################################

_change_lang_reply_EN = """
✅ Your language was modified successfully!
"""

_change_lang_reply_PT = """
✅ Seu idioma foi alterado com sucesso!
"""

change_lang_reply = {
    'EN': _change_lang_reply_EN,
    'PT': _change_lang_reply_PT}

###############################################################################

_welcome_reply_EN = """
Hello! I'm <b>CardaBot</b> 🤖, a Cardano information bot developed by <b>EveryBlock Studio</b> (ticker: <code>EBS</code>).

I'm not ready for the public yet 😞

These are the commands I understand for now:

/start
/poolinfo TICKER
/netinfo
/help
/language LANG
<code>   : LANG = [EN, PT]</code>

"""

_welcome_reply_PT = """
Olá! Sou o <b>CardaBot</b> 🤖, um bot de informações da rede Cardano desenvolvido pela <b>EveryBlock Studio</b> (ticker: <code>EBS</code>).

Ainda não estou pronto para o público 😞

Esses são os comandos que eu entendo por enquanto:

/start
/poolinfo TICKER
/netinfo
/help
/language LANG
<code>   : LANG = [EN, PT]</code>

"""

welcome_reply = {
    'EN': _welcome_reply_EN,
    'PT': _welcome_reply_PT}

###############################################################################

_help_reply_EN = """
These are the commands I understand for now:

/start
/poolinfo TICKER
/netinfo
/help
/language LANG
<code>   : LANG = [EN, PT]</code>

"""

_help_reply_PT = """
Esses são os comandos que eu entendo por enquanto:

/start
/poolinfo TICKER
/netinfo
/help
/language LANG
<code>   : LANG = [EN, PT]</code>
"""

help_reply = {
    'EN': _help_reply_EN,
    'PT': _help_reply_PT}
