_poolinfo_reply_EN = """
<b><code>{ticker}</code> {pool_name}</b>
<i>{desc}</i>
🌐{homepage}

<b>🆔 Pool ID</b>
<code>{pool_id}</code>

<b> ℹ️ Pool info</b>
    rank: <code>#️{pool_rank}</code>
    pledge: <code>{pledge} ₳</code>
    cost: <code>{cost} ₳</code>
    margin: <code>{margin_perc}%</code>

<b>📈 Metrics</b>
    saturation: <code>{saturat:.2f}% {saturat_symbol}</code>
    controlled stake: <code>{rel_stake_perc:.3f}%</code>
    active stake: <code>{active_stake} ₳</code>
      ↳ delegators: <code>{n_active_delegators}</code>
    live stake: <code>{live_stake} ₳</code>
      ↳ delegators: <code>{n_live_delegators}</code>

<b>🎲 Blocks</b>
    expected blocks (this /epoch): <code>~{expected_blocks:.1f}</code>
    lifetime blocks: <code>{blocks}{block_produced_symbol}</code>

<i>Live metrics updated {updated_time_ago} ago.</i>
"""
#    rewards: <code>{rewards} ₳</code>

_poolinfo_reply_PT = """
<b><code>{ticker}</code> {pool_name}</b>
<i>{desc}</i>
🌐{homepage}

<b>🆔 Identificador da pool</b>
<code>{pool_id}</code>

<b>ℹ️ Informações</b>
    rank: <code>#️{pool_rank}</code>
    pledge: <code>{pledge} ₳</code>
    custo: <code>{cost} ₳</code>
    margem: <code>{margin_perc}%</code>

<b>📈 Métricas</b>
    saturação: <code>{saturat:.2f}% {saturat_symbol}</code>
    stake controlado: <code>{rel_stake_perc:.3f}%</code>
    stake ativo: <code>{active_stake} ₳</code>
      ↳ delegadores: <code>{n_active_delegators}</code>
    stake atual: <code>{live_stake} ₳</code>
      ↳ delegadores: <code>{n_live_delegators}</code>

<b>🎲 Blocos</b>
    blocos esperados (nesta época): <code>~{expected_blocks:.1f}</code>
    total de blocos produzidos: <code>{blocks}{block_produced_symbol}</code>

<i>Métricas atualizadas {updated_time_ago} atrás.</i>
"""
# recompensas por ADA delegada: <code>{rewards} ₳</code>

_poolinfo_reply_KR = """
<b><code>{ticker}</code> {pool_name}</b>
<i>{desc}</i>
🌐{homepage}

<b>🆔 풀 식별자</b>
<code>{pool_id}</code>

<b>ℹ️ 풀 정보</b>
    순위: <code>#️{pool_rank}</code>
    담보량: <code>{pledge} ₳</code>
    풀고정수수료: <code>{cost} ₳</code>
    풀운영수수료: <code>{margin_perc}%</code>

<b>📈 상세정보</b>
    포화도: <code>{saturat:.2f}% {saturat_symbol}</code>
    위임점유율: <code>{rel_stake_perc:.3f}%</code>
    활성 위임량: <code>{active_stake} ₳</code>
      ↳ 위임자수: <code>{n_active_delegators}</code>
    현재 위임량: <code>{live_stake} ₳</code>
      ↳ 위임자수: <code>{n_live_delegators}</code>

<b>🎲 블록</b>
    예측 블록수 (해당 에포크): <code>~{expected_blocks:.1f}</code>
    총 생성 블록수: <code>{blocks}{block_produced_symbol}</code>


<i>실시간 메트릭스 업데이트 {updated_time_ago} 전</i>
"""
#    보상: <code>{rewards} ₳</code>


_poolinfo_reply_JP = """
<b><code>{ticker}</code> {pool_name}</b>
<i>{desc}</i>
🌐{homepage}

<b>🆔 プール識別子</b>
<code>{pool_id}</code>

<b>ℹ️ プール情報</b>
    順位: <code>#️{pool_rank}</code>
    担保量: <code>{pledge} ₳</code>
    プール固定手数料: <code>{cost} ₳</code>
    プール運営手数料: <code>{margin_perc}%</code>

<b>📈 メトリックス</b>
    飽和度: <code>{saturat:.2f}% {saturat_symbol}</code>
    現在ステーキング占め率: <code>{rel_stake_perc:.3f}%</code>
    活性委任量: <code>{active_stake} ₳</code>
      ↳ 委任者数: <code>{n_active_delegators}</code>
    現在委任量: <code>{live_stake} ₳</code>
      ↳ 委任者数: <code>{n_live_delegators}</code>

<b>🎲 ブロック</b>
    予測ブロック数 (当該エポクの): <code>~{expected_blocks:.1f}</code>
    生成ブロックの総数: <code>{blocks}{block_produced_symbol}</code>

<i>ライブメトリックスアップデート{updated_time_ago} 前</i>
"""
#    報酬: <code>{rewards} ₳</code>

poolinfo_reply = {
    "EN": _poolinfo_reply_EN,
    "PT": _poolinfo_reply_PT,
    "KR": _poolinfo_reply_KR,
    "JP": _poolinfo_reply_JP,
}

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
ごめんなさい。<code>{ticker}</code>プールが見つかりません 😞
"""

poolinfo_reply_error = {
    "EN": _poolinfo_reply_error_EN,
    "PT": _poolinfo_reply_error_PT,
    "KR": _poolinfo_reply_error_KR,
    "JP": _poolinfo_reply_error_JP,
}

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
今検索中。もう少しお待ちを… ⌛
"""

poolinfo_reply_wait = {
    "EN": _poolinfo_reply_wait_EN,
    "PT": _poolinfo_reply_wait_PT,
    "KR": _poolinfo_reply_wait_KR,
    "JP": _poolinfo_reply_wait_JP,
}

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
✅ 日本語への変更ができました!
"""

change_lang_reply = {
    "EN": _change_lang_reply_EN,
    "PT": _change_lang_reply_PT,
    "KR": _change_lang_reply_KR,
    "JP": _change_lang_reply_JP,
}


###############################################################################

_change_default_pool_reply_EN = """
✅ Your default pool was modified successfully!
"""

_change_default_pool_reply_PT = """
✅ Sua pool padrão foi alterada com sucesso!
"""

_change_default_pool_reply_KR = """
✅ 기본 풀 변경에 성공했습니다!
"""

_change_default_pool_reply_JP = """
✅ デフォルトプールが変更されました!
"""

change_default_pool_reply = {
    "EN": _change_default_pool_reply_EN,
    "PT": _change_default_pool_reply_PT,
    "KR": _change_default_pool_reply_KR,
    "JP": _change_default_pool_reply_JP,
}

###############################################################################

_welcome_reply_EN = """
Hello! I'm <b>CardaBot</b> 🤖, a Cardano information bot developed by <b>EveryBlock Studio</b> (ticker: <code>EBS</code>).

These are the commands I understand for now:

/start
/pool TICKER
/epoch
/help
/language LANG
<code>   : LANG = [EN, PT, JP, KR]</code>
"""

_welcome_reply_PT = """
Olá! Sou o <b>CardaBot</b> 🤖, um bot de informações da rede Cardano desenvolvido pela <b>EveryBlock Studio</b> (ticker: <code>EBS</code>).

Esses são os comandos que eu entendo por enquanto:

/start
/pool TICKER
/epoch
/help
/language LANG
<code>   : LANG = [EN, PT, JP, KR]</code>
"""

_welcome_reply_KR = """
안녕하세요 저는  <b>CardaBot</b> 🤖입니다.  저는 <b>EveryBlock Studio</b> (ticker: <code>EBS</code>) 개발된 카르다노 정보 봇입니다.

아래의 명령어를 입력하실 수 있습니다.

/start
/pool 풀 티커
/epoch
/help
/language 언어
<code>   : LANG = [EN, PT, JP, KR]</code>
"""

_welcome_reply_JP = """
こんにちは! 私は <b>CardaBot</b> 🤖です。 私は <b>EveryBlock Studio</b> (ticker: <code>EBS</code>)が開発したカルダノ情報ボットです。

現在、以下のコマンドが入力できます:

/start
/pool プールティッカー
/epoch
/help
/language 言語
<code>   : LANG = [EN, PT, JP, KR]</code>
"""

welcome_reply = {
    "EN": _welcome_reply_EN,
    "PT": _welcome_reply_PT,
    "KR": _welcome_reply_KR,
    "JP": _welcome_reply_JP,
}

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
現在、以下のコマンドが入力できます:

/start
/pool プールティッカー
/epoch
/help
/language 言語
<code>   : LANG = [EN, PT, JP, KR]</code>
"""

help_reply = {
    "EN": _help_reply_EN,
    "PT": _help_reply_PT,
    "KR": _help_reply_KR,
    "JP": _help_reply_JP,
}

###############################################################################

_epoch_reply_EN = """
🔄 <b>Epoch progress</b>
<code>{progress_bar} {perc:.1f}%</code>
    current epoch: <code>{current_epoch}</code>
    blocks: <code>{current_block}/21600</code>
    remaining time: <code>{remaining_time}</code>

💰 <b>Stake info</b>
    active stake: <code>{active_stake} ₳</code>
"""

_epoch_reply_PT = """
🔄 <b>Progresso da época</b>
<code>{progress_bar} {perc:.1f}%</code>
    época atual: <code>{current_epoch}</code>
    blocos: <code>{current_block}/21600</code>
    tempo restante: <code>{remaining_time}</code>

💰 <b>Informação do stake</b>
    stake ativo: <code>{active_stake} ₳</code>
"""

_epoch_reply_KR = """
🔄 <b>에포크 진행 상황</b>
<code>{progress_bar} {perc:.1f}%</code>
    현재 에포크: <code>{current_epoch}</code>
    블록수: <code>{current_block}/21600</code>
    에포크 남은 시간: <code>{remaining_time}</code>

💰 <b>위임 정보</b>
    활성 위임량: <code>{active_stake} ₳</code>
"""

_epoch_reply_JP = """
🔄 <b>エポク状況</b>
<code>{progress_bar} {perc:.1f}%</code>
    現在のエポク: <code>{current_epoch}</code>
    ブロック数: <code>{current_block}/21600</code>
    エポク残り時間: <code>{remaining_time}</code>

💰 <b>委任量情報</b>
    活性委任量: <code>{active_stake} ₳</code>
"""

epoch_reply = {
    "EN": _epoch_reply_EN,
    "PT": _epoch_reply_PT,
    "KR": _epoch_reply_KR,
    "JP": _epoch_reply_JP,
}

###############################################################################

_day_text_EN = "day"
_day_text_PT = "dia"
_day_text_KR = "일"
_day_text_JP = "日"

day_text = {
    "EN": _day_text_EN,
    "PT": _day_text_PT,
    "KR": _day_text_KR,
    "JP": _day_text_JP,
}

###############################################################################

_days_text_EN = "days"
_days_text_PT = "dias"
_days_text_KR = "일"
_days_text_JP = "日"

days_text = {
    "EN": _days_text_EN,
    "PT": _days_text_PT,
    "KR": _days_text_KR,
    "JP": _days_text_JP,
}

supported_languages = ["EN", "PT", "KR", "JP"]
