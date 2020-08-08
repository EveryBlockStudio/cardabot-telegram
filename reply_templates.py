_poolinfo_reply_EN = """
<b><code>{ticker}</code> {pool_name}</b>
<i>{desc}</i>
🌐{homepage}

<b>ℹ️ Pool info</b>
    rank: <code>#️{pool_rank} (random)</code>
    pledge: <code>{pledge_ada} ₳</code>
    cost: <code>{cost_ada} ₳</code>
    margin: <code>{margin_perc}%</code>

<b>📈 Metrics</b>
    saturation: <code>{saturat:.3f}%</code>
    controlled stake: <code>{rel_stake_perc}%</code>
    produced blocks: <code>{blocks}</code>
    rewards: <code>{rewards_ada} ₳</code>
"""

_poolinfo_reply_PT = """
<b><code>{ticker}</code> {pool_name}</b>
<i>{desc}</i>
🌐{homepage}

<b>ℹ️ Informações da pool</b>
    rank: <code>#️{pool_rank} (aleatório)</code>
    pledge: <code>{pledge_ada} ₳</code>
    custo: <code>{cost_ada} ₳</code>
    margem: <code>{margin_perc}%</code>

<b>📈 Métricas</b>
    saturação: <code>{saturat:.3f}%</code>
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
Hello! I'm <b>CardaBot</b> 🤖, a Cardano information bot developed by <b>EveryBlock Studio</b> (ticker: <code>EBS</code>) in collaboration with <b>@BradaPool</b> (ticker: <code>BRADA</code>).

These are the commands I understand for now:

/start
/pool TICKER
/epoch
/help
/language LANG
<code>   : LANG = [EN, PT]</code>
"""

_welcome_reply_PT = """
Olá! Sou o <b>CardaBot</b> 🤖, um bot de informações da rede Cardano desenvolvido pela <b>EveryBlock Studio</b> (ticker: <code>EBS</code>) em colaboração com a <b>@BradaPool</b> (ticker: <code>BRADA</code>).

Esses são os comandos que eu entendo por enquanto:

/start
/pool TICKER
/epoch
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
/pool TICKER
/epoch
/help
/language LANG
<code>   : LANG = [EN, PT]</code>

"""

_help_reply_PT = """
Esses são os comandos que eu entendo por enquanto:

/start
/pool TICKER
/epoch
/help
/language LANG
<code>   : LANG = [EN, PT]</code>
"""

help_reply = {
    'EN': _help_reply_EN,
    'PT': _help_reply_PT}

###############################################################################

_epoch_reply_EN = """
Here what I got:

🔄 <b>Epoch progress</b>
<code>{progress_bar} {perc:.1f}%</code>
    Current epoch: <code>{current_epoch}</code>
    Slots: <code>{current_slot}/432000</code>
    Remaining time: <code>{remaining_time}</code>
"""

_epoch_reply_PT = """
Aqui o que eu encontrei:

🔄 <b>Progresso da época</b>
<code>{progress_bar} {perc:.1f}%</code>
    Época atual: <code>{current_epoch}</code>
    Slots: <code>{current_slot}/432000</code>
    Tempo restante: <code>{remaining_time}</code>
"""

epoch_reply = {
    'EN': _epoch_reply_EN,
    'PT': _epoch_reply_PT}

###############################################################################

_day_text_EN = "day"
_day_text_PT = "dia"

day_text = {
    'EN': _day_text_EN,
    'PT': _day_text_PT}

###############################################################################

_days_text_EN = "days"
_days_text_PT = "dias"

days_text = {
    'EN': _days_text_EN,
    'PT': _days_text_PT}
