from typing import Mapping

from pink_accents import Accent


class Ork(Accent):
    """Warhammer40K Ork zpeech"""

    WORDS = {
        r"would have": "woulda",
        r"let me": "lemme",
        r"give me": "gimme",
        r"have to": "hafta",
        r"(mech suits|mechs)": "mekks",
        r"again": "agin",
        r"(and|and)": "an'",
        r"and": "an’",
        r"another": "annuver",
        r"best": "bestest",
        r"bolts": "bits",
        r"boys": "Boyz",
        r"(bunch|group)": "lot",
        r"can": "kan",
        r"captain": "kap'n",
        r"catch": "ketch",
        r"(chopper|helicopter)": "kopta",
        r"(choppers|helicopters)": "koptas",
        r"company": "comp'ny",
        r"containers": "boxez",
        r"(correct|proper)": "proppa",
        r"cunning": "kunnin'",
        r"for": "fer",
        r"fuck": "fokk",
        r"galaxy": "galuxy",
        r"gasoline": "guzzolene",
        r"(get|guy|girl)": "git",
        r"got": "gots",
        r"guns": "shootaz",
        r"half": "‘af",
        r"(he|he)": "'e",
        r"he": "‘e",
        r"(head|mind)": "'ead",
        r"heads": "'eadz",
        r"(hey|hi)": "oy",
        r"(him|them)": "'im",
        r"him": "‘em",
        r"how": "'ow",
        r"(humans|people|mankind)": "'umies",
        r"humans": "‘umiez",
        r"i'm": "Iz",
        r"(in|in)": "'n",
        r"in": "‘n",
        r"junk": "skrap",
        r"lieutenant": "lootenant",
        r"liquor": "likker",
        r"little": "lil",
        r"maybe": "mebbe",
        r"mechs": "meks",
        r"money": "munny",
        r"(money|teeth|cash|coin|payment|pay|dollars|dollar|pesos|peso|yen|euros|euro|pence)": "teef",
        r"my": "ma",
        r"never": "neva",
        r"(of|of)": "uv",
        r"(old|old)": "ol'",
        r"old": "ol",
        r"(one|one)": "wun",
        r"other": "uvva",
        r"pretty": "purty",
        r"(say|says)": "sez",
        r"soldier": "soldja",
        r"soldiers": "soldjas",
        r"something": "sumfin",
        r"swords": "choppaz",
        r"technology": "gubbinz",
        r"(technology|tech)": "teknologee",
        r"(that|what|what)": "wot",
        r"that": "‘dat",
        r"(the|the)": "da",
        r"the": "‘da",
        r"things": "fings",
        r"(to|to)": "ta",
        r"(truck|truck)": "trukk",
        r"war": "waugh",
        r"(war|waagh|waa)": "WAAAGH!",
        r"was": "wuz",
        r"with": "wit'",
        r"women": "wimmen",
        r"(you|you)": "ya",
        r"(you|your|your)": "yer",
        r"human race": "puny 'umies",
        r"couple of": "coupla",
        r"(i ran away|i had to escape|i ran from them|i got away from him|i got away from her|i go away from them)": "I ran, but Orks are never beaten in battle… we can always come back for annuver go,",
        r"(we ran away|we had to run away|we had to escape|we ran from them|we got away from them)": "we ran, but Orks are never beaten in battle… we can always come back for annuver go,",
        r"out of": "outta",
        r"going to": "Gunna",
        r"to the head": "to the drops",
        r"(mens room|men's room|womens room|women's room|ladies room|lady's room|boy's room|boys room|bathroom|restroom|lavatory|potty)": "drops",
        r"her": "‘er",
        r"that's": "‘dats",
        r"there": "‘der",
        r"their": "‘dere",
        r"human": "‘umie",
        r"bang": "dakka",
        r"(bang|shots)": "daka",
        r"particular": "partic’lar",
        r"thing": "fing",
        r"trucks": "trukks",
        r"trucker": "mek boy",
        r"truckers": "mek boyz",
        r"lover": "luvva",
        r"lovers": "luvvas",
        r"just": "jus’",
        r"has": "‘as",
        r"fight": "fight",
        r"fighting": "fight'n'",
        r"battle": "WAAGH!",
        r"(tussle|duel|confrontation|skirmish|quarrel)": "scrap",
        r"(defeat|rout|beat)": "smash",
        r"defeat": "stompn",
        r"defeating": "stomp'n",
        r"defeated": "stomped",
        r"rout": "Smash",
        r"killing": "stomp'n'",
        r"(flashy|wealth)": "flash",
        r"rich": "snobby ",
        r"wealthy": "snobby",
        r"scorch": "skorch",
        r"them": "im",
        r"three": "tree",
        r"killed": "kilt",
        r"this": "‘dis",
        r"mech": "mek",
        r"claw": "klaw",
        r"claws": "klaws",
        r"gods": "Godz",
        r"themselves": "demselves",
        r"im": "I'z",
        r"think": "fink",
        r"through": "throo",
        r"show": "showz",
        r"good": "gud",
        r"because": "'cos",
        r"who": "'oo",
        r"here": "‘ere",
        r"cool": "kool",
        r"death": "deth",
        r"engine": "enjin",
        r"engines": "enjinz",
        r"first": "furst",
        r"is": "iz",
        r"except": "'sept",
        r"does": "duz",
        r"honest": "‘onest",
        r"thought": "thought",
        r"thoughts": "thoughtz",
        r"suns": "sunz",
        r"(whatshisname|whatsitsname|whatchamacallit)": "wossname",
        r"(customization|customizing)": "kustomizin",
        r"teleport": "tellyport",
        r"teleporter": "tellyporta",
        r"teleported": "tellyported",
        r"barrel": "barrul",
        r"barrels": "barrulz",
        r"mechanic": "mekaniak ",
        r"(what'sit|whatsit)": "wotsit",
    }
    PATTERNS = {
        r"\bth": "d",
        r"\bca": "ka",
        r"\bcu": "ku",
        r"\bco": "ko",
        r"\bcr": "kr",
        r"\bex": "'",
        r"th\b": "d",
        r"ca\b": "ka",
        r"cu\b": "ku",
        r"co\b": "ko",
        r"cr\b": "kr",
        r"ex\b": "'",
    }


if __name__ == "__main__":
    # generate accent from website data, can be found in html
    inputs = (
        # https://lingojam.com/Warhammer40KOrkTranslator
        {
            "phrases1": "would have\nlet me\ngive me\nhave to\nmech suits",
            "phrases2": "woulda\nlemme\ngimme\nhafta\nmekks",
            "words1": "again\nand\nanother\nbest\nbolts\nboys\nbunch\ncan\ncaptain\ncatch\nchopper\nchoppers\ncompany\ncontainers\ncorrect\ncunning\nfor\nfuck\ngalaxy\ngasoline\nget\ngot\ngroup\nguns\nhalf\nhe\nhead\nheads\nhelicopter\nhelicopters\nhey\nhi\nhim\nhow\nhumans\ni'm\nin\njunk\nlieutenant\nliquor\nlittle\nmaybe\nmechs\nmind\nmoney\nmy\nnever\nof\nold\none\nother\npeople\npretty\nproper\nsay\nsays\nsoldier\nsoldiers\nsomething\nswords\ntechnology\nteeth\nthat\nthe\nthings\nto\ntruck\nwar\nwas\nwhat\nwith\nwomen\nyou\nyour",
            "words2": "agin\nan'\nanuvva\nbestest\nbits\nboyz\nlot\nkin\nkap'n\nketch\nkopta\nkoptas\ncomp'ny\nboxez\nproppa\nkunn'n'\nfer\nfokk\ngaluxy\nguzzolene\ngit\ngots\nlot\nshootaz\n'aff\n'e\n'ead\n'eadz\nkopta\nkoptas\noy\noy\n'im\n'ow\n'umies\ni'z\n'n\nskrap\nlootenant\nlikker\nlil\nmebbe\nmekks\n'ead\nmunny\nmah\nneva\nuv\nol'\nwun\nuvva\n'umies\npurty\nproppa\nsez\nsez\nsoldja\nsoldjas\nsumfin\nchoppaz\ngubbinz\nteef\nwot\nda\nstuff\nta\ntrukk\nwaugh\nwuz\nwot\nwit\nwimmen\nya\nyer",
            "intraword1": "",
            "intraword2": "",
            "prefixes1": "",
            "prefixes2": "",
            "suffixes1": "ing\ner\ners",
            "suffixes2": "'n'\na\naz",
            "regex1": "",
            "regex2": "",
            "rev_regex1": "",
            "rev_regex2": "",
            "ordering1": "",
            "ordering2": "",
        },
        # https://lingojam.com/WarhammerOrkTranzlator
        {
            "phrases1": "human race\ncouple of\nI ran away\nwe ran away\nwe had to run away\nwe had to escape\nI had to escape\nwe ran from them\nI ran from them\nI got away from him\nI got away from her\nWe got away from them\nI go away from them\nout of\ngoing to\nGoing to\nto the head\nMens room\nMen's room\nWomens room\nWomen's room\nladies room\nlady's room\nboy's room\nboys room",
            "phrases2": "puny 'umies\ncoupla\nI ran, but Orks are never beaten in battle\u2026 we can always come back for annuver go,\nwe ran, but Orks are never beaten in battle\u2026 we can always come back for annuver go,\nwe ran, but Orks are never beaten in battle\u2026 we can always come back for annuver go,\nwe ran, but Orks are never beaten in battle\u2026 we can always come back for annuver go,\nI ran, but Orks are never beaten in battle\u2026 we can always come back for annuver go,\nwe ran, but Orks are never beaten in battle\u2026 we can always come back for annuver go,\nI ran, but Orks are never beaten in battle\u2026 we can always come back for annuver go,\nI ran, but Orks are never beaten in battle\u2026 we can always come back for annuver go,\nI ran, but Orks are never beaten in battle\u2026 we can always come back for annuver go,\nwe ran, but Orks are never beaten in battle\u2026 we can always come back for annuver go,\nI ran, but Orks are never beaten in battle\u2026 we can always come back for annuver go,\noutta\ngunna\nGunna\nto the drops\ndrops\ndrops\ndrops\ndrops\ndrops\ndrops\ndrops\ndrops",
            "words1": "the\nthe\nthe\nand\nand\nand\nyou\nyou\nin\nin\nher\nher\nhim\nhim\nthat\nthat\nthat\nthat's\nthat's\nthat's\nmy\nthere\nthere\nthere\ntheir\ntheir\ntheir\nhuman\nhuman\nhuman\nhumans\nhumans\nhumans\nwar\nwaagh\nwaa\nbang\nbang\nbang\nparticular\nthing\nthings\ntruck\ntrucks\ntrucker\ntruckers\nlover\nlovers\njust\njust\njust\nof\nwhat\nhas\nhas\nguy\ngirl\nfight\nfighting\nbattle\ntussle\nduel\nconfrontation\nskirmish\nquarrel\ntechnology\ntech\ndefeat\ndefeat\ndefeating\ndefeated\nrout\nRout\nbeat\nkilling\nflashy\nrich\nwealth\nwealthy\nmoney\ncash\ncoin\npayment\npay\ndollars\ndollar\npesos\npeso\nyen\neuros\neuro\npence\nboys\nscorch\nthem\nthem\nhalf\nhalf\nhalf\nthree\nkilled\nthis\nthis\nthis\nhe\nhe\nmech\nmechs\nclaw\nclaws\nwith\nwith\ngods\nanother\nthemselves\ncan\ncunning\nyour\nI'm\nIm\nI'm\nthink\nthrough\nshow\ngood\nold\nold\nbecause\nwho\nhere\nhere\nhere\nbathroom\nrestroom\nlavatory\npotty\ncool\nto\ndeath\nengine\nengines\nfirst\nshots\nis\nexcept\none\ndoes\nhonest\nhonest\nhonest\nthought\nthoughts\nmankind\nsuns\nwhatshisname\nwhatsitsname\nwhatchamacallit\ncustomization\ncustomizing\nteleport\nteleporter\nteleported\nbarrel\nbarrels\nmechanic\nwhat'sit\nwhatsit",
            "words2": "da\n'da\n\u2018da\nan'\nan\nan\u2019\nya\nyer\n'n\n\u2018n\n'er\n\u2018er\n'em\n\u2018em\ndat\n'dat\n\u2018dat\ndats\n'dats\n\u2018dats\nma\nder\n'der\n\u2018der\ndere\n'dere\n\u2018dere\numie\n'umie\n\u2018umie\n'umiez\nummiez\n\u2018umiez\nWAAAGH!\nWAAAGH!\nWAAAGH!\ndaka daka daka!\ndaka\ndakka\npartic\u2019lar\nfing\nfings\ntrukk\ntrukks\nmek boy\nmek boyz\nluvva\nluvvas\njus' \njus\njus\u2019\nuv\nwot\n'as\n\u2018as\ngit\ngit\nfight\nfight'n'\nWAAGH!\nscrap\nscrap\nscrap\nscrap\nscrap\nteknologee\nteknologee\nsmash\nstompn\nstomp'n\nstomped\nsmash\nSmash\nsmash\nstomp'n'\nflash\nsnobby \nflash\nsnobby\nteef\nteef\nteef\nteef\nteef\nteef\nteef\nteef\nteef\nteef\nteef\nteef\nteef\nBoyz\nskorch\n'im\nim\n'af\naf\n\u2018af\ntree\nkilt\n'dis\ndis\n\u2018dis\n'e\n\u2018e\nmek\nmeks\nklaw\nklaws\nwiv \nwit'\nGodz\nannuver\ndemselves\nkan\nkunnin'\nyer\nIz\nI'z\nI'z\nfink\nthroo\nshowz\ngud\nol'\nol\n'cos\n'oo\n'ere\nere\n\u2018ere\ndrops\ndrops\ndrops\ndrops\nkool\nta\ndeth\nenjin\nenjinz\nfurst\ndaka\niz\n'sept\nwun\nduz\n'onest\nonest\n\u2018onest\nthought\nthoughtz\n'umies\nsunz\nwossname\nwossname\nwossname\nkustomizin\nkustomizin\ntellyport\ntellyporta\ntellyported\nbarrul\nbarrulz\nmekaniak \nwotsit\nwotsit",
            "intraword1": "",
            "intraword2": "",
            "prefixes1": "th\nca\ncu\nco\ncr\nex",
            "prefixes2": "d\nka\nku\nko\nkr\n'",
            "suffixes1": "er\ners\ners\nies\ning\ning\nthy\n is",
            "suffixes2": "a\naz\nas\niez\n'n\n'n'\nty\n'z",
            "regex1": "",
            "regex2": "",
            "rev_regex1": "",
            "rev_regex2": "",
            "ordering1": "",
            "ordering2": "",
        },
    )

    words = {}
    patterns = {}

    def push(key: str, value: str, collection: Mapping[str, str]):
        # lower keys are fine, lower values are not
        key = key.lower()
        lower_value = value.lower()

        if (existing := collection.get(key)) is None:
            collection[key] = value
        elif isinstance(existing, str):
            collection[key] = [existing, value]
        else:
            # avoid adding replacements for different letter cases, a few of these are
            # present in input data
            for i in collection[key]:
                if i.lower() == lower_value:
                    break
            else:
                collection[key].append(value)

    for inp in inputs:
        # split in advance
        for k, v in inp.items():
            if (splitted := v.split("\n")) == [""]:
                splitted = []

            inp[k] = splitted

        word_keys = {
            "phrases1": "phrases2",
            "words1": "words2",
        }

        for k, v in word_keys.items():
            for word, replacement in zip(inp[k], inp[v]):
                push(word, replacement, words)

        prefix_keys = {
            "prefixes1": "prefixes2",
        }

        for k, v in prefix_keys.items():
            for prefix, replacement in zip(inp[k], inp[v]):
                push(fr"\b{prefix}", replacement, patterns)

        suffix_keys = {
            "suffixes1": "suffixes2",
        }

        for k, v in prefix_keys.items():
            for suffix, replacement in zip(inp[k], inp[v]):
                push(fr"{suffix}\b", replacement, patterns)

    # merge duplicated values in single regex
    inverted_words_map = {}
    for k, v in words.items():
        if isinstance(v, list):
            values = v
        else:
            values = [v]

        for v in values:
            if v in inverted_words_map:
                inverted_words_map[v].append(k)
            else:
                inverted_words_map[v] = [k]

    words = {
        f'({"|".join(words)})' if len(words) > 1 else words[0]: replacement
        for replacement, words in inverted_words_map.items()
    }

    print("WORDS = {")
    for k, v in words.items():
        if isinstance(v, str):
            print(f'r"{k}": "{v}",')
        else:
            print(f"""r"{k}": ({",".join(f'"{i}"' for i in v)},),""")
    print("}")

    print("PATTERNS = {")
    for k, v in patterns.items():
        if isinstance(v, str):
            print(f'r"{k}": "{v}",')
        else:
            print(f"""r"{k}": ({", ".join(f'"{i}"' for i in v)},),""")
    print("}")
