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

_poolinfo_reply_KR = """
<b><code>{ticker}</code> {pool_name}</b>
<i>{desc}</i>
🌐{homepage}

<b>ℹ️ 풀 정보</b>
    순위: <code>#️{pool_rank} (랜덤)</code>
    담보량: <code>{pledge_ada} ₳</code>
    고정수수료: <code>{cost_ada} ₳</code>
    상대수수료: <code>{margin_perc}%</code>

<b>📈 상세정보</b>
    포화도: <code>{saturat:.3f}%</code>
    위임량: <code>{rel_stake_perc}%</code>
    생성 블록 수: <code>{blocks}</code>
    보상: <code>{rewards_ada} ₳</code>
"""

_poolinfo_reply_JP = """
<b><code>{ticker}</code> {pool_name}</b>
<i>{desc}</i>
🌐{homepage}

<b>ℹ️ プール情報</b>
    ランク: <code>#️{pool_rank} (random)</code>
    誓約（資本）: <code>{pledge_ada} ₳</code>
    固定費: <code>{cost_ada} ₳</code>
    変動費: <code>{margin_perc}%</code>

<b>📈 メトリクス</b>
    飽和: <code>{saturat:.3f}%</code>
    委託量: <code>{rel_stake_perc}%</code>
    生成ブロック: <code>{blocks}</code>
    報酬: <code>{rewards_ada} ₳</code>
"""

poolinfo_reply = {
    'EN': _poolinfo_reply_EN,
    'PT': _poolinfo_reply_PT,
    'KR': _poolinfo_reply_KR,
    'JP': _poolinfo_reply_JP}

###############################################################################

_poolinfo_reply_error_EN = """
Sorry, I didn't find the <code>{ticker}</code> pool 😞
"""

_poolinfo_reply_error_PT = """
Desculpa, não achei a pool <code>{ticker}</code> 😞
"""

_poolinfo_reply_error_KR = """
죄송합니다 풀 <code>{ticker}</code> 를 찾을 수 없습니다 😞
"""

_poolinfo_reply_error_JP = """
ごめんなさい！ <code>{ticker}</code> プールは見つかりませんでした 😞
"""

poolinfo_reply_error = {
    'EN': _poolinfo_reply_error_EN,
    'PT': _poolinfo_reply_error_PT,
    'KR': _poolinfo_reply_error_KR,
    'JP': _poolinfo_reply_error_JP}

###############################################################################

_poolinfo_reply_wait_EN = """
I'm searching for the pool, one moment please... ⌛
"""

_poolinfo_reply_wait_PT = """
Estou procurando a pool, um momento por favor... ⌛
"""

_poolinfo_reply_wait_KR = """
풀을 검색하는 중... 조금만 기다려 주세요. ⌛
"""

_poolinfo_reply_wait_JP = """
プールを探しています、少々お待ちください... ⌛
"""

poolinfo_reply_wait = {
    'EN': _poolinfo_reply_wait_EN,
    'PT': _poolinfo_reply_wait_PT,
    'KR': _poolinfo_reply_wait_KR,
    'JP': _poolinfo_reply_wait_JP}

###############################################################################

_change_lang_reply_EN = """
✅ Your language was modified successfully!
"""

_change_lang_reply_PT = """
✅ Seu idioma foi alterado com sucesso!
"""

_change_lang_reply_KR = """
✅ 한국어로의 전환이 성공했습니다!
"""

_change_lang_reply_JP = """
✅ 言語の切り替えに成功しました!
"""

change_lang_reply = {
    'EN': _change_lang_reply_EN,
    'PT': _change_lang_reply_PT,
    'KR': _change_lang_reply_KR,
    'JP': _change_lang_reply_JP}

###############################################################################

_welcome_reply_EN = """
Hello! I'm <b>CardaBot</b> 🤖, a Cardano information bot developed by <b>EveryBlock Studio</b> (ticker: <code>EBS</code>) in collaboration with <b>@BradaPool</b> (ticker: <code>BRADA</code>).

These are the commands I understand for now:

/start
/pool TICKER
/epoch
/help
/language LANG
<code>   : LANG = [EN, PT, JP, KR]</code>
"""

_welcome_reply_PT = """
Olá! Sou o <b>CardaBot</b> 🤖, um bot de informações da rede Cardano desenvolvido pela <b>EveryBlock Studio</b> (ticker: <code>EBS</code>) em colaboração com a <b>@BradaPool</b> (ticker: <code>BRADA</code>).

Esses são os comandos que eu entendo por enquanto:

/start
/pool TICKER
/epoch
/help
/language LANG
<code>   : LANG = [EN, PT, JP, KR]</code>
"""

_welcome_reply_KR = """
안녕하세요 저는  <b>CardaBot</b> 🤖입니다.  저는 <b>EveryBlock Studio</b> (ticker: <code>EBS</code>) 와 @BradaPool (ticker: <code>BRADA</code>) 의 협업으로 개발된 카르다노 정보 봇입니다.

아래의 명령어를 입력하실 수 있습니다.

/start
/pool 풀 티커
/epoch
/help
/language 언어
<code>   : LANG = [EN, PT, JP, KR]</code>
"""

_welcome_reply_JP = """
こんにちは! 私は <b>CardaBot</b> 🤖です。 私は @Bradapool (ticker: <code>BRADA</code>) との協同により<b>EveryBlock Studio</b> (ticker: <code>EBS</code>)が開発したカルダノ情報ボットです。

いま使えるコマンドはこちらです。:

/start
/pool ティッカー
/epoch
/help
/language 言語
<code>   : LANG = [EN, PT, JP, KR]</code>
"""

welcome_reply = {
    'EN': _welcome_reply_EN,
    'PT': _welcome_reply_PT,
    'KR': _welcome_reply_KR,
    'JP': _welcome_reply_JP}

###############################################################################

_help_reply_EN = """
These are the commands I understand for now:

/start
/pool TICKER
/epoch
/help
/language LANG
<code>   : LANG = [EN, PT, JP, KR]</code>

"""

_help_reply_PT = """
Esses são os comandos que eu entendo por enquanto:

/start
/pool TICKER
/epoch
/help
/language LANG
<code>   : LANG = [EN, PT, JP, KR]</code>
"""

_help_reply_KR = """
아래의 명령어를 입력하실 수 있습니다.

/start
/pool 풀 티커
/epoch
/help
/language 언어
<code>   : LANG = [EN, PT, JP, KR]</code>
"""

_help_reply_JP = """
いま使えるコマンドはこちらです。:

/start
/pool ティッカー
/epoch
/help
/language 言語
<code>   : LANG = [EN, PT, JP, KR]</code>
"""

help_reply = {
    'EN': _help_reply_EN,
    'PT': _help_reply_PT,
    'KR': _help_reply_KR,
    'JP': _help_reply_JP}

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

_epoch_reply_KR = """
검색 결과:

🔄 <b>에포크 진행 상황</b>
<code>{progress_bar} {perc:.1f}%</code>
    현재 에포크: <code>{current_epoch}</code>
    슬롯: <code>{current_slot}/432000</code>
    에포크 남은 시간: <code>{remaining_time}</code>
"""

_epoch_reply_JP = """
取得した情報:

🔄 <b>エポックの進捗</b>
<code>{progress_bar} {perc:.1f}%</code>
    現在のエポック: <code>{current_epoch}</code>
    スロット: <code>{current_slot}/432000</code>
    残りの期間: <code>{remaining_time}</code>
"""

epoch_reply = {
    'EN': _epoch_reply_EN,
    'PT': _epoch_reply_PT,
    'KR': _epoch_reply_KR,
    'JP': _epoch_reply_JP}

###############################################################################

_day_text_EN = "day"
_day_text_PT = "dia"
_day_text_KR = "일"
_day_text_JP = "日"

day_text = {
    'EN': _day_text_EN,
    'PT': _day_text_PT,
    'KR': _day_text_KR,
    'JP': _day_text_JP}

###############################################################################

_days_text_EN = "days"
_days_text_PT = "dias"
_days_text_KR = "일"
_days_text_JP = "日"

days_text = {
    'EN': _days_text_EN,
    'PT': _days_text_PT,
    'KR': _days_text_KR,
    'JP': _days_text_JP}
