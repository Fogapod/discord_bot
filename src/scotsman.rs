use crate::accent::Accent;
use crate::replacement::{DirectTarget, Replacement, Source};
pub struct Scotsman {
    replacements: Vec<Replacement>,
}

impl Accent for Scotsman {
    fn replacements(&self) -> &[Replacement] {
        &self.replacements
    }
}

impl Scotsman {
    pub fn new() -> Self {
        Self {
            replacements: vec![
                Replacement::new(
                    Source::Raw(r"$(?<!```)\z"),
                    Box::new(DirectTarget {
                        replacement: " ye daft cunt",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\babout\b"),
                    Box::new(DirectTarget {
                        replacement: "aboot",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\babove\b"),
                    Box::new(DirectTarget {
                        replacement: "`boon",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\baccounts\b"),
                    Box::new(DirectTarget {
                        replacement: "accoonts",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bacross\b"),
                    Box::new(DirectTarget {
                        replacement: "o`er",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bafter\b"),
                    Box::new(DirectTarget {
                        replacement: "efter",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bagree\b"),
                    Box::new(DirectTarget {
                        replacement: "gree",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\ball\b"),
                    Box::new(DirectTarget { replacement: "aw" }),
                ),
                Replacement::new(
                    Source::Raw(r"\balmost\b"),
                    Box::new(DirectTarget {
                        replacement: "a`maist",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\balong\b"),
                    Box::new(DirectTarget {
                        replacement: "alang",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\balready\b"),
                    Box::new(DirectTarget {
                        replacement: "awready",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\balso\b"),
                    Box::new(DirectTarget {
                        replacement: "an` a`",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\balthough\b"),
                    Box::new(DirectTarget {
                        replacement: "althoogh",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\band\b"),
                    Box::new(DirectTarget { replacement: "`n`" }),
                ),
                Replacement::new(
                    Source::Raw(r"\banother\b"),
                    Box::new(DirectTarget {
                        replacement: "anither",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bany\b"),
                    Box::new(DirectTarget { replacement: "ony" }),
                ),
                Replacement::new(
                    Source::Raw(r"\banyone\b"),
                    Box::new(DirectTarget {
                        replacement: "a`body",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\banybody\b"),
                    Box::new(DirectTarget {
                        replacement: "a`body",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\banything\b"),
                    Box::new(DirectTarget {
                        replacement: "anythin`",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\barrested\b"),
                    Box::new(DirectTarget {
                        replacement: "liftit",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\barrest\b"),
                    Box::new(DirectTarget {
                        replacement: "lift",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\barrests\b"),
                    Box::new(DirectTarget {
                        replacement: "lifts",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bargues\b"),
                    Box::new(DirectTarget {
                        replacement: "argies",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bargued\b"),
                    Box::new(DirectTarget {
                        replacement: "argied",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bargue\b"),
                    Box::new(DirectTarget {
                        replacement: "argie",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\baround\b"),
                    Box::new(DirectTarget {
                        replacement: "aroond",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bavailable\b"),
                    Box::new(DirectTarget {
                        replacement: "free",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bavoiding\b"),
                    Box::new(DirectTarget {
                        replacement: "jookin",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bavoided\b"),
                    Box::new(DirectTarget {
                        replacement: "jooked",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bavoid\b"),
                    Box::new(DirectTarget {
                        replacement: "jook",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bask\b"),
                    Box::new(DirectTarget {
                        replacement: "spir",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bassistant\b"),
                    Box::new(DirectTarget {
                        replacement: "servand",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bassistants\b"),
                    Box::new(DirectTarget {
                        replacement: "servands",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\basking\b"),
                    Box::new(DirectTarget {
                        replacement: "spirin",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\basked\b"),
                    Box::new(DirectTarget {
                        replacement: "spire'd",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\baway\b"),
                    Box::new(DirectTarget {
                        replacement: "awa`",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bbabies\b"),
                    Box::new(DirectTarget {
                        replacement: "bairns",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bbaby\b"),
                    Box::new(DirectTarget {
                        replacement: "bairn",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bbad\b"),
                    Box::new(DirectTarget { replacement: "ill" }),
                ),
                Replacement::new(
                    Source::Raw(r"\bballs\b"),
                    Box::new(DirectTarget {
                        replacement: "baws",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bball\b"),
                    Box::new(DirectTarget { replacement: "baw" }),
                ),
                Replacement::new(
                    Source::Raw(r"\bbars\b"),
                    Box::new(DirectTarget {
                        replacement: "boozers",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bbar\b"),
                    Box::new(DirectTarget {
                        replacement: "boozer",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bbeen\b"),
                    Box::new(DirectTarget {
                        replacement: "buin",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bbeautiful\b"),
                    Box::new(DirectTarget {
                        replacement: "bonny",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bbecause\b"),
                    Box::new(DirectTarget { replacement: "fur" }),
                ),
                Replacement::new(
                    Source::Raw(r"\bbreakdown\b"),
                    Box::new(DirectTarget {
                        replacement: "breakdoon",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bnap\b"),
                    Box::new(DirectTarget { replacement: "kip" }),
                ),
                Replacement::new(
                    Source::Raw(r"\bnapping\b"),
                    Box::new(DirectTarget {
                        replacement: "kipin'",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bbefore\b"),
                    Box::new(DirectTarget {
                        replacement: "afore",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bbelieves\b"),
                    Box::new(DirectTarget {
                        replacement: "hawps",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bbelieving\b"),
                    Box::new(DirectTarget {
                        replacement: "hawpin",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bbelieve\b"),
                    Box::new(DirectTarget {
                        replacement: "hawp",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bbetween\b"),
                    Box::new(DirectTarget {
                        replacement: "atween",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bboards\b"),
                    Box::new(DirectTarget {
                        replacement: "boords",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bboard\b"),
                    Box::new(DirectTarget {
                        replacement: "boord",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bboth\b"),
                    Box::new(DirectTarget {
                        replacement: "baith",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bboxes\b"),
                    Box::new(DirectTarget {
                        replacement: "kists",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bbox\b"),
                    Box::new(DirectTarget {
                        replacement: "kist",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bboy\b"),
                    Box::new(DirectTarget {
                        replacement: "laddie",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bbrother\b"),
                    Box::new(DirectTarget {
                        replacement: "brither",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bbrothers\b"),
                    Box::new(DirectTarget {
                        replacement: "brithers",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bbut\b"),
                    Box::new(DirectTarget { replacement: "bit" }),
                ),
                Replacement::new(
                    Source::Raw(r"\bbitch\b"),
                    Box::new(DirectTarget {
                        replacement: "cunt",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bcaptain\b"),
                    Box::new(DirectTarget {
                        replacement: "caiptain",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bcap\b"),
                    Box::new(DirectTarget {
                        replacement: "caip",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bcalling\b"),
                    Box::new(DirectTarget {
                        replacement: "ca`ing",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bcalled\b"),
                    Box::new(DirectTarget {
                        replacement: "cawed",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bcall\b"),
                    Box::new(DirectTarget { replacement: "caw" }),
                ),
                Replacement::new(
                    Source::Raw(r"\bcars\b"),
                    Box::new(DirectTarget {
                        replacement: "motors",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bcar\b"),
                    Box::new(DirectTarget {
                        replacement: "motor",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bcared\b"),
                    Box::new(DirectTarget {
                        replacement: "car'd",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bcards\b"),
                    Box::new(DirectTarget {
                        replacement: "cairds",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bcard\b"),
                    Box::new(DirectTarget {
                        replacement: "caird",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bcareers\b"),
                    Box::new(DirectTarget {
                        replacement: "joabs",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bcareer\b"),
                    Box::new(DirectTarget {
                        replacement: "joab",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bcargo\b"),
                    Box::new(DirectTarget {
                        replacement: "cargae",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bcentury\b"),
                    Box::new(DirectTarget {
                        replacement: "hunner years",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bchanged\b"),
                    Box::new(DirectTarget {
                        replacement: "chaynged",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bchange\b"),
                    Box::new(DirectTarget {
                        replacement: "chaynge",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bchaplain\b"),
                    Box::new(DirectTarget {
                        replacement: "priestheid",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bchief\b"),
                    Box::new(DirectTarget {
                        replacement: "heid",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bchild\b"),
                    Box::new(DirectTarget {
                        replacement: "wee'un",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bchilderen\b"),
                    Box::new(DirectTarget {
                        replacement: "wee'uns",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bchoosing\b"),
                    Box::new(DirectTarget {
                        replacement: "walin",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bchoose\b"),
                    Box::new(DirectTarget {
                        replacement: "wale",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bchurches\b"),
                    Box::new(DirectTarget {
                        replacement: "kirks",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bchurch\b"),
                    Box::new(DirectTarget {
                        replacement: "kirk",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bcity\b"),
                    Box::new(DirectTarget {
                        replacement: "toon",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bcities\b"),
                    Box::new(DirectTarget {
                        replacement: "toons",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bcloser\b"),
                    Box::new(DirectTarget {
                        replacement: "claiser",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bclosest\b"),
                    Box::new(DirectTarget {
                        replacement: "claisest",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bclose\b"),
                    Box::new(DirectTarget {
                        replacement: "claise",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bclowns\b"),
                    Box::new(DirectTarget {
                        replacement: "clouns",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bclown\b"),
                    Box::new(DirectTarget {
                        replacement: "cloun",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bcoats\b"),
                    Box::new(DirectTarget {
                        replacement: "coaties",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bcoat\b"),
                    Box::new(DirectTarget {
                        replacement: "coatie",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bcoldest\b"),
                    Box::new(DirectTarget {
                        replacement: "cauldest",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bcolder\b"),
                    Box::new(DirectTarget {
                        replacement: "caulder",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bcold\b"),
                    Box::new(DirectTarget {
                        replacement: "cauld",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bcooks\b"),
                    Box::new(DirectTarget {
                        replacement: "keuks",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bcook\b"),
                    Box::new(DirectTarget {
                        replacement: "keuk",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bconsumer\b"),
                    Box::new(DirectTarget {
                        replacement: "punter",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bconsumers\b"),
                    Box::new(DirectTarget {
                        replacement: "punters",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bcould\b"),
                    Box::new(DirectTarget {
                        replacement: "cuid",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bcountries\b"),
                    Box::new(DirectTarget {
                        replacement: "lands",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bcountry\b"),
                    Box::new(DirectTarget {
                        replacement: "land",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bcourse\b"),
                    Box::new(DirectTarget {
                        replacement: "coorse",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bcourses\b"),
                    Box::new(DirectTarget {
                        replacement: "coorses",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bcultures\b"),
                    Box::new(DirectTarget {
                        replacement: "culchurs",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bculture\b"),
                    Box::new(DirectTarget {
                        replacement: "culchur",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bcustomer\b"),
                    Box::new(DirectTarget {
                        replacement: "punter",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bcustomers\b"),
                    Box::new(DirectTarget {
                        replacement: "punters",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bdaddy\b"),
                    Box::new(DirectTarget {
                        replacement: "daddie",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bdark\b"),
                    Box::new(DirectTarget {
                        replacement: "mirk",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bdad\b"),
                    Box::new(DirectTarget { replacement: "da" }),
                ),
                Replacement::new(
                    Source::Raw(r"\bdead\b"),
                    Box::new(DirectTarget {
                        replacement: "deid",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bdeaf\b"),
                    Box::new(DirectTarget {
                        replacement: "deav",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bdeafen\b"),
                    Box::new(DirectTarget {
                        replacement: "deave",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bdeafened\b"),
                    Box::new(DirectTarget {
                        replacement: "deaved",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bdebate\b"),
                    Box::new(DirectTarget {
                        replacement: "argie",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bdebating\b"),
                    Box::new(DirectTarget {
                        replacement: "argiein",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bdebates\b"),
                    Box::new(DirectTarget {
                        replacement: "argies",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bdegrees\b"),
                    Box::new(DirectTarget {
                        replacement: "grees",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bdegree\b"),
                    Box::new(DirectTarget {
                        replacement: "gree",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bdetectives\b"),
                    Box::new(DirectTarget {
                        replacement: "snoots",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bdetective\b"),
                    Box::new(DirectTarget {
                        replacement: "snoot",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bdifficult\b"),
                    Box::new(DirectTarget {
                        replacement: "pernicketie",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bdinner\b"),
                    Box::new(DirectTarget { replacement: "tea" }),
                ),
                Replacement::new(
                    Source::Raw(r"\bdirectors\b"),
                    Box::new(DirectTarget {
                        replacement: "guiders",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bdirector\b"),
                    Box::new(DirectTarget {
                        replacement: "guider",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bdid\b"),
                    Box::new(DirectTarget {
                        replacement: "daed",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bdo\b"),
                    Box::new(DirectTarget { replacement: "dae" }),
                ),
                Replacement::new(
                    Source::Raw(r"\bdogs\b"),
                    Box::new(DirectTarget {
                        replacement: "dugs",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bdog\b"),
                    Box::new(DirectTarget { replacement: "dug" }),
                ),
                Replacement::new(
                    Source::Raw(r"\bdown\b"),
                    Box::new(DirectTarget {
                        replacement: "doon",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bdownricht\b"),
                    Box::new(DirectTarget {
                        replacement: "doun",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bdroped\b"),
                    Box::new(DirectTarget {
                        replacement: "draped",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bdrops\b"),
                    Box::new(DirectTarget {
                        replacement: "draps",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bdrop\b"),
                    Box::new(DirectTarget {
                        replacement: "drap",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bdrink\b"),
                    Box::new(DirectTarget {
                        replacement: "drappie",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bdrinking\b"),
                    Box::new(DirectTarget {
                        replacement: "swillin'",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bdrank\b"),
                    Box::new(DirectTarget {
                        replacement: "swilled",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bdrunk\b"),
                    Box::new(DirectTarget { replacement: "fou" }),
                ),
                Replacement::new(
                    Source::Raw(r"\bduring\b"),
                    Box::new(DirectTarget {
                        replacement: "while",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bdying\b"),
                    Box::new(DirectTarget {
                        replacement: "deein'",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\beach\b"),
                    Box::new(DirectTarget { replacement: "ilk" }),
                ),
                Replacement::new(
                    Source::Raw(r"\bearly\b"),
                    Box::new(DirectTarget {
                        replacement: "earlie",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\beating\b"),
                    Box::new(DirectTarget {
                        replacement: "slochin",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bate\b"),
                    Box::new(DirectTarget {
                        replacement: "sloched",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\beat\b"),
                    Box::new(DirectTarget {
                        replacement: "sloch",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bedges\b"),
                    Box::new(DirectTarget {
                        replacement: "lips",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bedge\b"),
                    Box::new(DirectTarget { replacement: "lip" }),
                ),
                Replacement::new(
                    Source::Raw(r"\benjoys\b"),
                    Box::new(DirectTarget {
                        replacement: "gilravages",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\benjoy\b"),
                    Box::new(DirectTarget {
                        replacement: "gilravage",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bengineer\b"),
                    Box::new(DirectTarget {
                        replacement: "navvy",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bengineering\b"),
                    Box::new(DirectTarget {
                        replacement: "ingineerin",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bengineers\b"),
                    Box::new(DirectTarget {
                        replacement: "Navvies",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bevenings\b"),
                    Box::new(DirectTarget {
                        replacement: "forenichts",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bevening\b"),
                    Box::new(DirectTarget {
                        replacement: "forenicht",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bevery\b"),
                    Box::new(DirectTarget {
                        replacement: "ilka",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\beverybody\b"),
                    Box::new(DirectTarget {
                        replacement: "a`body",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\beveryone\b"),
                    Box::new(DirectTarget {
                        replacement: "a`body",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\beye\b"),
                    Box::new(DirectTarget { replacement: "ee" }),
                ),
                Replacement::new(
                    Source::Raw(r"\beyes\b"),
                    Box::new(DirectTarget {
                        replacement: "e'ens",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bface\b"),
                    Box::new(DirectTarget {
                        replacement: "physog",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bfamililies\b"),
                    Box::new(DirectTarget {
                        replacement: "fowks",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bfamily\b"),
                    Box::new(DirectTarget {
                        replacement: "fowk",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bfast\b"),
                    Box::new(DirectTarget {
                        replacement: "fleet",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bfathers\b"),
                    Box::new(DirectTarget {
                        replacement: "faithers",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bfather\b"),
                    Box::new(DirectTarget {
                        replacement: "faither",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bfight\b"),
                    Box::new(DirectTarget {
                        replacement: "rammy",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bfighting\b"),
                    Box::new(DirectTarget {
                        replacement: "ramming",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bfights\b"),
                    Box::new(DirectTarget {
                        replacement: "rammies",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bfilms\b"),
                    Box::new(DirectTarget {
                        replacement: "pictures",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bfilm\b"),
                    Box::new(DirectTarget {
                        replacement: "picture",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bfinding\b"),
                    Box::new(DirectTarget {
                        replacement: "fin`ing",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bfound\b"),
                    Box::new(DirectTarget {
                        replacement: "fund",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bfine\b"),
                    Box::new(DirectTarget {
                        replacement: "braw",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bfloors\b"),
                    Box::new(DirectTarget {
                        replacement: "flairs",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bfloor\b"),
                    Box::new(DirectTarget {
                        replacement: "flair",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bfoods\b"),
                    Box::new(DirectTarget {
                        replacement: "fairns",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bfood\b"),
                    Box::new(DirectTarget {
                        replacement: "fairn",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bfor\b"),
                    Box::new(DirectTarget { replacement: "fer" }),
                ),
                Replacement::new(
                    Source::Raw(r"\bforget\b"),
                    Box::new(DirectTarget {
                        replacement: "forgoat",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bfriends\b"),
                    Box::new(DirectTarget {
                        replacement: "mukkers",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bfriend\b"),
                    Box::new(DirectTarget { replacement: "pal" }),
                ),
                Replacement::new(
                    Source::Raw(r"\bfrom\b"),
                    Box::new(DirectTarget { replacement: "fae" }),
                ),
                Replacement::new(
                    Source::Raw(r"\bfull\b"),
                    Box::new(DirectTarget {
                        replacement: "stowed oot",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bgames\b"),
                    Box::new(DirectTarget {
                        replacement: "gams",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bgame\b"),
                    Box::new(DirectTarget { replacement: "gam" }),
                ),
                Replacement::new(
                    Source::Raw(r"\bgardens\b"),
                    Box::new(DirectTarget {
                        replacement: "back greens",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bgarden\b"),
                    Box::new(DirectTarget {
                        replacement: "back green",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bget\b"),
                    Box::new(DirectTarget { replacement: "git" }),
                ),
                Replacement::new(
                    Source::Raw(r"\bgirl\b"),
                    Box::new(DirectTarget {
                        replacement: "lassie",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bgive\b"),
                    Box::new(DirectTarget { replacement: "gie" }),
                ),
                Replacement::new(
                    Source::Raw(r"\bglasses\b"),
                    Box::new(DirectTarget {
                        replacement: "glesses",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bglass\b"),
                    Box::new(DirectTarget {
                        replacement: "gless",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bgo\b"),
                    Box::new(DirectTarget { replacement: "gae" }),
                ),
                Replacement::new(
                    Source::Raw(r"\bgood\b"),
                    Box::new(DirectTarget {
                        replacement: "guid",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bgreat\b"),
                    Box::new(DirectTarget {
                        replacement: "stoatin",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bgrowing\b"),
                    Box::new(DirectTarget {
                        replacement: "grawing",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bgrown\b"),
                    Box::new(DirectTarget {
                        replacement: "grawn",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bgrow\b"),
                    Box::new(DirectTarget {
                        replacement: "graw",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bglared\b"),
                    Box::new(DirectTarget {
                        replacement: "glower'd",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bglaring\b"),
                    Box::new(DirectTarget {
                        replacement: "glowrin'",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bguess\b"),
                    Box::new(DirectTarget {
                        replacement: "jalouse",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bhad\b"),
                    Box::new(DirectTarget {
                        replacement: "haed",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bhas\b"),
                    Box::new(DirectTarget {
                        replacement: "haes",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bhadnt\b"),
                    Box::new(DirectTarget {
                        replacement: "haedna",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bhadn't\b"),
                    Box::new(DirectTarget {
                        replacement: "haedna",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bhairs\b"),
                    Box::new(DirectTarget {
                        replacement: "locks",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bhair\b"),
                    Box::new(DirectTarget {
                        replacement: "locks",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bhalfs\b"),
                    Box::new(DirectTarget {
                        replacement: "haufs",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bhalf\b"),
                    Box::new(DirectTarget {
                        replacement: "hauf",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bhands\b"),
                    Box::new(DirectTarget {
                        replacement: "hauns",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bhand\b"),
                    Box::new(DirectTarget {
                        replacement: "haun",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bhangs\b"),
                    Box::new(DirectTarget {
                        replacement: "hings",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bhanging\b"),
                    Box::new(DirectTarget {
                        replacement: "hinging",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bhang\b"),
                    Box::new(DirectTarget {
                        replacement: "hing",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bhave\b"),
                    Box::new(DirectTarget { replacement: "hae" }),
                ),
                Replacement::new(
                    Source::Raw(r"\bheads\b"),
                    Box::new(DirectTarget {
                        replacement: "heids",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bhead\b"),
                    Box::new(DirectTarget {
                        replacement: "heid",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bhearts\b"),
                    Box::new(DirectTarget {
                        replacement: "herts",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bheart\b"),
                    Box::new(DirectTarget {
                        replacement: "hert",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bhelp\b"),
                    Box::new(DirectTarget {
                        replacement: "hulp",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bhere\b"),
                    Box::new(DirectTarget {
                        replacement: "`ere",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bhigh\b"),
                    Box::new(DirectTarget {
                        replacement: "heich",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bhimself\b"),
                    Box::new(DirectTarget {
                        replacement: "his-sel",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bholding\b"),
                    Box::new(DirectTarget {
                        replacement: "hauding",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bhold\b"),
                    Box::new(DirectTarget {
                        replacement: "haud",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bhomes\b"),
                    Box::new(DirectTarget {
                        replacement: "hames",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bhome\b"),
                    Box::new(DirectTarget {
                        replacement: "hame",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bhopes\b"),
                    Box::new(DirectTarget {
                        replacement: "hawps",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bhope\b"),
                    Box::new(DirectTarget {
                        replacement: "hawp",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bhoter\b"),
                    Box::new(DirectTarget {
                        replacement: "heter",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bhotest\b"),
                    Box::new(DirectTarget {
                        replacement: "hetest",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bhot\b"),
                    Box::new(DirectTarget { replacement: "het" }),
                ),
                Replacement::new(
                    Source::Raw(r"\bhotels\b"),
                    Box::new(DirectTarget {
                        replacement: "change-hooses",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bhotel\b"),
                    Box::new(DirectTarget {
                        replacement: "change-hoose",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bhours\b"),
                    Box::new(DirectTarget {
                        replacement: "oors",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bhour\b"),
                    Box::new(DirectTarget { replacement: "oor" }),
                ),
                Replacement::new(
                    Source::Raw(r"\bhouse\b"),
                    Box::new(DirectTarget {
                        replacement: "hoose",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bhouses\b"),
                    Box::new(DirectTarget {
                        replacement: "hooses",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bhow\b"),
                    Box::new(DirectTarget { replacement: "hou" }),
                ),
                Replacement::new(
                    Source::Raw(r"\bhusband\b"),
                    Box::new(DirectTarget {
                        replacement: "guidman",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bimages\b"),
                    Box::new(DirectTarget {
                        replacement: "photies",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bimage\b"),
                    Box::new(DirectTarget {
                        replacement: "photie",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bimagine\b"),
                    Box::new(DirectTarget {
                        replacement: "jalouse",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bincluding\b"),
                    Box::new(DirectTarget {
                        replacement: "anaw",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bindicates\b"),
                    Box::new(DirectTarget {
                        replacement: "shows",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bindicate\b"),
                    Box::new(DirectTarget {
                        replacement: "show",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\binformations\b"),
                    Box::new(DirectTarget {
                        replacement: "speirins",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\binformation\b"),
                    Box::new(DirectTarget {
                        replacement: "speirins",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\binto\b"),
                    Box::new(DirectTarget {
                        replacement: "intae",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bits\b"),
                    Box::new(DirectTarget { replacement: "tis" }),
                ),
                Replacement::new(
                    Source::Raw(r"\bisn't\b"),
                    Box::new(DirectTarget {
                        replacement: "isna",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bisnt\b"),
                    Box::new(DirectTarget {
                        replacement: "isna",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bjanitors\b"),
                    Box::new(DirectTarget {
                        replacement: "jannies",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bjanitor\b"),
                    Box::new(DirectTarget {
                        replacement: "jannie",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bjobs\b"),
                    Box::new(DirectTarget {
                        replacement: "jabs",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bjoined\b"),
                    Box::new(DirectTarget {
                        replacement: "jyneed",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bjoins\b"),
                    Box::new(DirectTarget {
                        replacement: "jynes",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bjoin\b"),
                    Box::new(DirectTarget {
                        replacement: "jyne",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bjust\b"),
                    Box::new(DirectTarget {
                        replacement: "juist",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bkids\b"),
                    Box::new(DirectTarget {
                        replacement: "bairns",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bkid\b"),
                    Box::new(DirectTarget {
                        replacement: "bairn",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bkills\b"),
                    Box::new(DirectTarget {
                        replacement: "murdurrs",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bkiller\b"),
                    Box::new(DirectTarget {
                        replacement: "murdurrur",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bkilled\b"),
                    Box::new(DirectTarget {
                        replacement: "murdurred",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bkill\b"),
                    Box::new(DirectTarget {
                        replacement: "murdurr",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bkitchens\b"),
                    Box::new(DirectTarget {
                        replacement: "sculleries",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bkitchen\b"),
                    Box::new(DirectTarget {
                        replacement: "scullery",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bknows\b"),
                    Box::new(DirectTarget {
                        replacement: "kens",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bknow\b"),
                    Box::new(DirectTarget { replacement: "ken" }),
                ),
                Replacement::new(
                    Source::Raw(r"\bknown\b"),
                    Box::new(DirectTarget {
                        replacement: "kent",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\blanguages\b"),
                    Box::new(DirectTarget {
                        replacement: "leids",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\blanguage\b"),
                    Box::new(DirectTarget {
                        replacement: "leid",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\blarger\b"),
                    Box::new(DirectTarget {
                        replacement: "lairger",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\blargest\b"),
                    Box::new(DirectTarget {
                        replacement: "lairgest",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\blarge\b"),
                    Box::new(DirectTarget {
                        replacement: "lairge",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\blast\b"),
                    Box::new(DirectTarget {
                        replacement: "lest",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\blater\b"),
                    Box::new(DirectTarget {
                        replacement: "efter",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\blaughing\b"),
                    Box::new(DirectTarget {
                        replacement: "roarin",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\blaugh\b"),
                    Box::new(DirectTarget {
                        replacement: "roar",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\blawyers\b"),
                    Box::new(DirectTarget {
                        replacement: "advocates",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\blawyer\b"),
                    Box::new(DirectTarget {
                        replacement: "advocate",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\blead\b"),
                    Box::new(DirectTarget {
                        replacement: "leid",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bleading\b"),
                    Box::new(DirectTarget {
                        replacement: "leidin",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bleaving\b"),
                    Box::new(DirectTarget {
                        replacement: "leaing",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bleave\b"),
                    Box::new(DirectTarget { replacement: "lea" }),
                ),
                Replacement::new(
                    Source::Raw(r"\blet\b"),
                    Box::new(DirectTarget {
                        replacement: "loot",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\blegs\b"),
                    Box::new(DirectTarget {
                        replacement: "shanks",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bleg\b"),
                    Box::new(DirectTarget {
                        replacement: "shank",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bdevil\b"),
                    Box::new(DirectTarget {
                        replacement: "deuce",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bdevils\b"),
                    Box::new(DirectTarget {
                        replacement: "deuces",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\blying\b"),
                    Box::new(DirectTarget {
                        replacement: "liein",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\blike\b"),
                    Box::new(DirectTarget {
                        replacement: "lik`",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\blikely\b"),
                    Box::new(DirectTarget {
                        replacement: "likelie",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\blittle\b"),
                    Box::new(DirectTarget { replacement: "wee" }),
                ),
                Replacement::new(
                    Source::Raw(r"\blonger\b"),
                    Box::new(DirectTarget {
                        replacement: "langer",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\blongest\b"),
                    Box::new(DirectTarget {
                        replacement: "langest",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\blong\b"),
                    Box::new(DirectTarget {
                        replacement: "lang",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\blooking\b"),
                    Box::new(DirectTarget {
                        replacement: "keeking",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\blooked\b"),
                    Box::new(DirectTarget {
                        replacement: "keeked",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\blook\b"),
                    Box::new(DirectTarget {
                        replacement: "keek",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bloved\b"),
                    Box::new(DirectTarget {
                        replacement: "loued",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bloving\b"),
                    Box::new(DirectTarget {
                        replacement: "louing",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\blove\b"),
                    Box::new(DirectTarget {
                        replacement: "loue",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bmakes\b"),
                    Box::new(DirectTarget {
                        replacement: "mak`s",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bmake\b"),
                    Box::new(DirectTarget {
                        replacement: "mak`",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bmen\b"),
                    Box::new(DirectTarget {
                        replacement: "jimmies",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bmanage\b"),
                    Box::new(DirectTarget {
                        replacement: "guide",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bmanagers\b"),
                    Box::new(DirectTarget {
                        replacement: "high heid yins",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bmanager\b"),
                    Box::new(DirectTarget {
                        replacement: "high heid yin",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bmany\b"),
                    Box::new(DirectTarget {
                        replacement: "mony",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bmay\b"),
                    Box::new(DirectTarget { replacement: "mey" }),
                ),
                Replacement::new(
                    Source::Raw(r"\bmarkets\b"),
                    Box::new(DirectTarget {
                        replacement: "merkats",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bmarket\b"),
                    Box::new(DirectTarget {
                        replacement: "merkat",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bmarriages\b"),
                    Box::new(DirectTarget {
                        replacement: "mairriages",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bmarriage\b"),
                    Box::new(DirectTarget {
                        replacement: "mairriage",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bmatters\b"),
                    Box::new(DirectTarget {
                        replacement: "maiters",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bmatter\b"),
                    Box::new(DirectTarget {
                        replacement: "maiter",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bmaybe\b"),
                    Box::new(DirectTarget {
                        replacement: "mibbie",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bmeetings\b"),
                    Box::new(DirectTarget {
                        replacement: "meetins",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bmeeting\b"),
                    Box::new(DirectTarget {
                        replacement: "meetin",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bmethods\b"),
                    Box::new(DirectTarget {
                        replacement: "ways",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bmethod\b"),
                    Box::new(DirectTarget { replacement: "way" }),
                ),
                Replacement::new(
                    Source::Raw(r"\bmight\b"),
                    Box::new(DirectTarget {
                        replacement: "micht",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bmind\b"),
                    Box::new(DirectTarget {
                        replacement: "mynd",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bminer\b"),
                    Box::new(DirectTarget {
                        replacement: "pickman",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bminers\b"),
                    Box::new(DirectTarget {
                        replacement: "pickmen",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bmoney\b"),
                    Box::new(DirectTarget {
                        replacement: "dosh",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bmonths\b"),
                    Box::new(DirectTarget {
                        replacement: "munths",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bmonth\b"),
                    Box::new(DirectTarget {
                        replacement: "munth",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bmore\b"),
                    Box::new(DirectTarget {
                        replacement: "mair",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bmornings\b"),
                    Box::new(DirectTarget {
                        replacement: "mornin`s",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bmorning\b"),
                    Box::new(DirectTarget {
                        replacement: "mornin`",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bmost\b"),
                    Box::new(DirectTarget {
                        replacement: "maist",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bmothers\b"),
                    Box::new(DirectTarget {
                        replacement: "mithers",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bmother\b"),
                    Box::new(DirectTarget {
                        replacement: "mither",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bmouths\b"),
                    Box::new(DirectTarget {
                        replacement: "geggies",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bmouth\b"),
                    Box::new(DirectTarget {
                        replacement: "geggy",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bmoves\b"),
                    Box::new(DirectTarget {
                        replacement: "shifts",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bmove\b"),
                    Box::new(DirectTarget {
                        replacement: "shift",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bmuch\b"),
                    Box::new(DirectTarget {
                        replacement: "muckle",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bmust\b"),
                    Box::new(DirectTarget {
                        replacement: "mist",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bmy\b"),
                    Box::new(DirectTarget { replacement: "ma" }),
                ),
                Replacement::new(
                    Source::Raw(r"\bmyself\b"),
                    Box::new(DirectTarget {
                        replacement: "masell",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bnasty\b"),
                    Box::new(DirectTarget {
                        replacement: "mingin",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bnetworks\b"),
                    Box::new(DirectTarget {
                        replacement: "netwurks",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bnetwork\b"),
                    Box::new(DirectTarget {
                        replacement: "netwurk",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bnever\b"),
                    Box::new(DirectTarget {
                        replacement: "ne`er",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bnew\b"),
                    Box::new(DirectTarget {
                        replacement: "freish",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bnews\b"),
                    Box::new(DirectTarget {
                        replacement: "speirins",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bnext\b"),
                    Box::new(DirectTarget {
                        replacement: "neist",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bnice\b"),
                    Box::new(DirectTarget {
                        replacement: "crakin`",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bnights\b"),
                    Box::new(DirectTarget {
                        replacement: "nichts",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bnight\b"),
                    Box::new(DirectTarget {
                        replacement: "nicht",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bFalse\b"),
                    Box::new(DirectTarget { replacement: "na" }),
                ),
                Replacement::new(
                    Source::Raw(r"\bnot\b"),
                    Box::new(DirectTarget { replacement: "nae" }),
                ),
                Replacement::new(
                    Source::Raw(r"\bnothing\b"),
                    Box::new(DirectTarget {
                        replacement: "neithin'",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bnow\b"),
                    Box::new(DirectTarget { replacement: "noo" }),
                ),
                Replacement::new(
                    Source::Raw(r"\bnumbers\b"),
                    Box::new(DirectTarget {
                        replacement: "nummers",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bnumber\b"),
                    Box::new(DirectTarget {
                        replacement: "nummer",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bof\b"),
                    Box::new(DirectTarget { replacement: "o`" }),
                ),
                Replacement::new(
                    Source::Raw(r"\boffices\b"),
                    Box::new(DirectTarget {
                        replacement: "affices",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\boffice\b"),
                    Box::new(DirectTarget {
                        replacement: "affice",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bofficers\b"),
                    Box::new(DirectTarget {
                        replacement: "boabies",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bofficer\b"),
                    Box::new(DirectTarget {
                        replacement: "boaby",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\boften\b"),
                    Box::new(DirectTarget {
                        replacement: "aften",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\boh\b"),
                    Box::new(DirectTarget { replacement: "och" }),
                ),
                Replacement::new(
                    Source::Raw(r"\bok\b"),
                    Box::new(DirectTarget {
                        replacement: "a`richt",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bold\b"),
                    Box::new(DirectTarget {
                        replacement: "auld",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\boil\b"),
                    Box::new(DirectTarget { replacement: "ile" }),
                ),
                Replacement::new(
                    Source::Raw(r"\bonce\b"),
                    Box::new(DirectTarget {
                        replacement: "wance",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bone\b"),
                    Box::new(DirectTarget { replacement: "wan" }),
                ),
                Replacement::new(
                    Source::Raw(r"\bonly\b"),
                    Box::new(DirectTarget {
                        replacement: "ainlie",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bother\b"),
                    Box::new(DirectTarget {
                        replacement: "ither",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bothers\b"),
                    Box::new(DirectTarget {
                        replacement: "ithers",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bours\b"),
                    Box::new(DirectTarget {
                        replacement: "oors",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bour\b"),
                    Box::new(DirectTarget { replacement: "oor" }),
                ),
                Replacement::new(
                    Source::Raw(r"\bout\b"),
                    Box::new(DirectTarget { replacement: "oot" }),
                ),
                Replacement::new(
                    Source::Raw(r"\boutside\b"),
                    Box::new(DirectTarget {
                        replacement: "ootdoors",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bover\b"),
                    Box::new(DirectTarget {
                        replacement: "ower",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bowns\b"),
                    Box::new(DirectTarget {
                        replacement: "ains",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bown\b"),
                    Box::new(DirectTarget { replacement: "ain" }),
                ),
                Replacement::new(
                    Source::Raw(r"\bowners\b"),
                    Box::new(DirectTarget {
                        replacement: "gaffers",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bowner\b"),
                    Box::new(DirectTarget {
                        replacement: "gaffer",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bpaintings\b"),
                    Box::new(DirectTarget {
                        replacement: "pentins",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bpainting\b"),
                    Box::new(DirectTarget {
                        replacement: "pentin",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bparts\b"),
                    Box::new(DirectTarget {
                        replacement: "pairts",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bpart\b"),
                    Box::new(DirectTarget {
                        replacement: "pairt",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bpartners\b"),
                    Box::new(DirectTarget {
                        replacement: "bidies",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bpartner\b"),
                    Box::new(DirectTarget {
                        replacement: "bidie",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bparty\b"),
                    Box::new(DirectTarget {
                        replacement: "pairtie",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bpass\b"),
                    Box::new(DirectTarget {
                        replacement: "bygae",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bpast\b"),
                    Box::new(DirectTarget {
                        replacement: "bygane",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bpeoples\b"),
                    Box::new(DirectTarget {
                        replacement: "fowks",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bpeople\b"),
                    Box::new(DirectTarget {
                        replacement: "fowk",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bperhaps\b"),
                    Box::new(DirectTarget {
                        replacement: "mibbie",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bperson\b"),
                    Box::new(DirectTarget {
                        replacement: "body",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bphones\b"),
                    Box::new(DirectTarget {
                        replacement: "phanes",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bphone\b"),
                    Box::new(DirectTarget {
                        replacement: "phane",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bplaces\b"),
                    Box::new(DirectTarget {
                        replacement: "steids",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bplace\b"),
                    Box::new(DirectTarget {
                        replacement: "steid",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bplays\b"),
                    Box::new(DirectTarget {
                        replacement: "speils",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bplay\b"),
                    Box::new(DirectTarget {
                        replacement: "speil",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bpolice\b"),
                    Box::new(DirectTarget {
                        replacement: "polis",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bpoor\b"),
                    Box::new(DirectTarget {
                        replacement: "brassic",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bpopular\b"),
                    Box::new(DirectTarget {
                        replacement: "weel-kent",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bproblems\b"),
                    Box::new(DirectTarget {
                        replacement: "kinches",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bproblem\b"),
                    Box::new(DirectTarget {
                        replacement: "kinch",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bprofessionals\b"),
                    Box::new(DirectTarget {
                        replacement: "perfaissionals",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bprofessional\b"),
                    Box::new(DirectTarget {
                        replacement: "perfaissional",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bprograms\b"),
                    Box::new(DirectTarget {
                        replacement: "progrums",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bprogram\b"),
                    Box::new(DirectTarget {
                        replacement: "progrum",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bprovides\b"),
                    Box::new(DirectTarget {
                        replacement: "gies",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bprovide\b"),
                    Box::new(DirectTarget { replacement: "gie" }),
                ),
                Replacement::new(
                    Source::Raw(r"\bprison\b"),
                    Box::new(DirectTarget {
                        replacement: "preeson",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bImprisonment\b"),
                    Box::new(DirectTarget {
                        replacement: "impreesonment",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bprisoner\b"),
                    Box::new(DirectTarget {
                        replacement: "preesoner",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bput\b"),
                    Box::new(DirectTarget { replacement: "pat" }),
                ),
                Replacement::new(
                    Source::Raw(r"\bquestions\b"),
                    Box::new(DirectTarget {
                        replacement: "quaistions",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bquestion\b"),
                    Box::new(DirectTarget {
                        replacement: "quaistion",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bquite\b"),
                    Box::new(DirectTarget {
                        replacement: "ferr",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bradios\b"),
                    Box::new(DirectTarget {
                        replacement: "trannies",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bradio\b"),
                    Box::new(DirectTarget {
                        replacement: "tranny",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\brather\b"),
                    Box::new(DirectTarget {
                        replacement: "ower",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bready\b"),
                    Box::new(DirectTarget {
                        replacement: "duin",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\breally\b"),
                    Box::new(DirectTarget {
                        replacement: "pure",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bred\b"),
                    Box::new(DirectTarget { replacement: "rid" }),
                ),
                Replacement::new(
                    Source::Raw(r"\brelationships\b"),
                    Box::new(DirectTarget {
                        replacement: "kinships",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\brelationship\b"),
                    Box::new(DirectTarget {
                        replacement: "kinship",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bremember\b"),
                    Box::new(DirectTarget {
                        replacement: "mind",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bremembered\b"),
                    Box::new(DirectTarget {
                        replacement: "minded",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\brights\b"),
                    Box::new(DirectTarget {
                        replacement: "richts",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bright\b"),
                    Box::new(DirectTarget {
                        replacement: "richt",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\broles\b"),
                    Box::new(DirectTarget {
                        replacement: "parts",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\brole\b"),
                    Box::new(DirectTarget {
                        replacement: "part",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bround\b"),
                    Box::new(DirectTarget {
                        replacement: "ruund",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bsame\b"),
                    Box::new(DirectTarget {
                        replacement: "identical",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bschools\b"),
                    Box::new(DirectTarget {
                        replacement: "schuils",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bschool\b"),
                    Box::new(DirectTarget {
                        replacement: "schuil",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bscores\b"),
                    Box::new(DirectTarget {
                        replacement: "hampden roars",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bscore\b"),
                    Box::new(DirectTarget {
                        replacement: "hampden roar",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bscuffed\b"),
                    Box::new(DirectTarget {
                        replacement: "scotched",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bseasons\b"),
                    Box::new(DirectTarget {
                        replacement: "seezins",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bseason\b"),
                    Box::new(DirectTarget {
                        replacement: "seezin",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bsecurity\b"),
                    Box::new(DirectTarget {
                        replacement: "polis",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bseconds\b"),
                    Box::new(DirectTarget {
                        replacement: "seiconts",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bsecond\b"),
                    Box::new(DirectTarget {
                        replacement: "seicont",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bseveral\b"),
                    Box::new(DirectTarget {
                        replacement: "loads",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bshaked\b"),
                    Box::new(DirectTarget {
                        replacement: "shoogled",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bshakes\b"),
                    Box::new(DirectTarget {
                        replacement: "shoogles",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bshake\b"),
                    Box::new(DirectTarget {
                        replacement: "shoogle",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bshould\b"),
                    Box::new(DirectTarget {
                        replacement: "shuid",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bshows\b"),
                    Box::new(DirectTarget {
                        replacement: "shaws",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bshowed\b"),
                    Box::new(DirectTarget {
                        replacement: "shawed",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bshow\b"),
                    Box::new(DirectTarget {
                        replacement: "shaw",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bsince\b"),
                    Box::new(DirectTarget { replacement: "sin" }),
                ),
                Replacement::new(
                    Source::Raw(r"\bsmall\b"),
                    Box::new(DirectTarget { replacement: "wee" }),
                ),
                Replacement::new(
                    Source::Raw(r"\bspoke\b"),
                    Box::new(DirectTarget {
                        replacement: "spak",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bso\b"),
                    Box::new(DirectTarget { replacement: "sae" }),
                ),
                Replacement::new(
                    Source::Raw(r"\bsoldiers\b"),
                    Box::new(DirectTarget {
                        replacement: "fighters",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bsoldier\b"),
                    Box::new(DirectTarget {
                        replacement: "fighter",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bsometimes\b"),
                    Box::new(DirectTarget {
                        replacement: "whiles",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bsomewhat\b"),
                    Box::new(DirectTarget {
                        replacement: "somewhit",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bsouth\b"),
                    Box::new(DirectTarget {
                        replacement: "sooth",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bsore\b"),
                    Box::new(DirectTarget {
                        replacement: "sair",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bstands\b"),
                    Box::new(DirectTarget {
                        replacement: "stauns",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bstand\b"),
                    Box::new(DirectTarget {
                        replacement: "staun",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bstars\b"),
                    Box::new(DirectTarget {
                        replacement: "starns",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bstar\b"),
                    Box::new(DirectTarget {
                        replacement: "starn",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bstarts\b"),
                    Box::new(DirectTarget {
                        replacement: "stairts",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bstart\b"),
                    Box::new(DirectTarget {
                        replacement: "stairt",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bstays\b"),
                    Box::new(DirectTarget {
                        replacement: "bides",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bstay\b"),
                    Box::new(DirectTarget {
                        replacement: "bade",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bstops\b"),
                    Box::new(DirectTarget {
                        replacement: "stoaps",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bstop\b"),
                    Box::new(DirectTarget {
                        replacement: "stoap",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bstores\b"),
                    Box::new(DirectTarget {
                        replacement: "hains",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bstore\b"),
                    Box::new(DirectTarget {
                        replacement: "hain",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bstruck\b"),
                    Box::new(DirectTarget {
                        replacement: "strak",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bstreets\b"),
                    Box::new(DirectTarget {
                        replacement: "wynds",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bstreet\b"),
                    Box::new(DirectTarget {
                        replacement: "wynd",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bstrong\b"),
                    Box::new(DirectTarget {
                        replacement: "pure tough",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bstyles\b"),
                    Box::new(DirectTarget {
                        replacement: "pure classes",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bstyle\b"),
                    Box::new(DirectTarget {
                        replacement: "pure class",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bsuch\b"),
                    Box::new(DirectTarget { replacement: "sic" }),
                ),
                Replacement::new(
                    Source::Raw(r"\btable\b"),
                    Box::new(DirectTarget {
                        replacement: "buird",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\btables\b"),
                    Box::new(DirectTarget {
                        replacement: "buirds",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\btakes\b"),
                    Box::new(DirectTarget {
                        replacement: "tak`s",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\btake\b"),
                    Box::new(DirectTarget {
                        replacement: "tak`",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\btalks\b"),
                    Box::new(DirectTarget {
                        replacement: "blethers",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\btalk\b"),
                    Box::new(DirectTarget {
                        replacement: "blether",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\btasks\b"),
                    Box::new(DirectTarget {
                        replacement: "hings",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\btask\b"),
                    Box::new(DirectTarget {
                        replacement: "hing",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bteams\b"),
                    Box::new(DirectTarget {
                        replacement: "gangs",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bteam\b"),
                    Box::new(DirectTarget {
                        replacement: "gang",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\btelevisions\b"),
                    Box::new(DirectTarget {
                        replacement: "tellyboxes",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\btelevision\b"),
                    Box::new(DirectTarget {
                        replacement: "tellybox",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bterminal\b"),
                    Box::new(DirectTarget {
                        replacement: "terminus",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bthe\b"),
                    Box::new(DirectTarget { replacement: "th`" }),
                ),
                Replacement::new(
                    Source::Raw(r"\btheir\b"),
                    Box::new(DirectTarget {
                        replacement: "thair",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bthem\b"),
                    Box::new(DirectTarget {
                        replacement: "thaim",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bthere\b"),
                    Box::new(DirectTarget {
                        replacement: "thare",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bthese\b"),
                    Box::new(DirectTarget {
                        replacement: "thae",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bthey\b"),
                    Box::new(DirectTarget {
                        replacement: "thay",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bthings\b"),
                    Box::new(DirectTarget {
                        replacement: "hings",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bthing\b"),
                    Box::new(DirectTarget {
                        replacement: "hing",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bthose\b"),
                    Box::new(DirectTarget {
                        replacement: "they",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bthrough\b"),
                    Box::new(DirectTarget {
                        replacement: "thro`",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bthroughout\b"),
                    Box::new(DirectTarget {
                        replacement: "throo`oot",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bthrow\b"),
                    Box::new(DirectTarget {
                        replacement: "chuck",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bthrew\b"),
                    Box::new(DirectTarget {
                        replacement: "chucked",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bto\b"),
                    Box::new(DirectTarget { replacement: "tae" }),
                ),
                Replacement::new(
                    Source::Raw(r"\btoday\b"),
                    Box::new(DirectTarget {
                        replacement: "th`day",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\btogether\b"),
                    Box::new(DirectTarget {
                        replacement: "th`gither",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\btonight\b"),
                    Box::new(DirectTarget {
                        replacement: "th`nicht",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\btoo\b"),
                    Box::new(DirectTarget { replacement: "tae" }),
                ),
                Replacement::new(
                    Source::Raw(r"\btold\b"),
                    Box::new(DirectTarget {
                        replacement: "telt",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\btops\b"),
                    Box::new(DirectTarget {
                        replacement: "taps",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\btop\b"),
                    Box::new(DirectTarget { replacement: "tap" }),
                ),
                Replacement::new(
                    Source::Raw(r"\btotal\b"),
                    Box::new(DirectTarget { replacement: "tot" }),
                ),
                Replacement::new(
                    Source::Raw(r"\btowns\b"),
                    Box::new(DirectTarget {
                        replacement: "touns",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\btown\b"),
                    Box::new(DirectTarget {
                        replacement: "toun",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\btough\b"),
                    Box::new(DirectTarget {
                        replacement: "hard",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\btraitors\b"),
                    Box::new(DirectTarget {
                        replacement: "quislings",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\btraitor\b"),
                    Box::new(DirectTarget {
                        replacement: "quisling",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\btroubles\b"),
                    Box::new(DirectTarget {
                        replacement: "trauchles",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\btrouble\b"),
                    Box::new(DirectTarget {
                        replacement: "trauchle",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bturds\b"),
                    Box::new(DirectTarget {
                        replacement: "jobbies",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bturd\b"),
                    Box::new(DirectTarget {
                        replacement: "jobbie",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bturn\b"),
                    Box::new(DirectTarget { replacement: "caw" }),
                ),
                Replacement::new(
                    Source::Raw(r"\bTVs\b"),
                    Box::new(DirectTarget {
                        replacement: "tellies",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bTV\b"),
                    Box::new(DirectTarget {
                        replacement: "telly",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\btwo\b"),
                    Box::new(DirectTarget { replacement: "twa" }),
                ),
                Replacement::new(
                    Source::Raw(r"\bunderstand\b"),
                    Box::new(DirectTarget { replacement: "ken" }),
                ),
                Replacement::new(
                    Source::Raw(r"\buntil\b"),
                    Box::new(DirectTarget {
                        replacement: "`til",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\buses\b"),
                    Box::new(DirectTarget {
                        replacement: "uises",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\buse\b"),
                    Box::new(DirectTarget {
                        replacement: "uise",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\busually\b"),
                    Box::new(DirectTarget {
                        replacement: "forordinar",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bvery\b"),
                    Box::new(DirectTarget { replacement: "gey" }),
                ),
                Replacement::new(
                    Source::Raw(r"\bvictims\b"),
                    Box::new(DirectTarget {
                        replacement: "sittin` ducks",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bvictim\b"),
                    Box::new(DirectTarget {
                        replacement: "sittin` duck",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bviews\b"),
                    Box::new(DirectTarget {
                        replacement: "sichts",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bview\b"),
                    Box::new(DirectTarget {
                        replacement: "sicht",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bwas\b"),
                    Box::new(DirectTarget { replacement: "wis" }),
                ),
                Replacement::new(
                    Source::Raw(r"\bwasn't\b"),
                    Box::new(DirectTarget {
                        replacement: "wisna",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bwasnt\b"),
                    Box::new(DirectTarget {
                        replacement: "wisna",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bwalks\b"),
                    Box::new(DirectTarget {
                        replacement: "daunders",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bwalk\b"),
                    Box::new(DirectTarget {
                        replacement: "daunder",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bwalked\b"),
                    Box::new(DirectTarget {
                        replacement: "daundered",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bwalking\b"),
                    Box::new(DirectTarget {
                        replacement: "daunderin",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bwall\b"),
                    Box::new(DirectTarget {
                        replacement: "dyke",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bwant\b"),
                    Box::new(DirectTarget {
                        replacement: "waant",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bwater\b"),
                    Box::new(DirectTarget {
                        replacement: "watter",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bway\b"),
                    Box::new(DirectTarget { replacement: "wey" }),
                ),
                Replacement::new(
                    Source::Raw(r"\bwarden\b"),
                    Box::new(DirectTarget {
                        replacement: "screw",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bwell\b"),
                    Box::new(DirectTarget {
                        replacement: "weel",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bwere\b"),
                    Box::new(DirectTarget { replacement: "war" }),
                ),
                Replacement::new(
                    Source::Raw(r"\bwest\b"),
                    Box::new(DirectTarget {
                        replacement: "wast",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bwhat\b"),
                    Box::new(DirectTarget {
                        replacement: "whit",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bwhatever\b"),
                    Box::new(DirectTarget {
                        replacement: "whitevur",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bwhen\b"),
                    Box::new(DirectTarget {
                        replacement: "whin",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bwhere\b"),
                    Box::new(DirectTarget {
                        replacement: "whaur",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bwhether\b"),
                    Box::new(DirectTarget {
                        replacement: "whither",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bwhich\b"),
                    Box::new(DirectTarget {
                        replacement: "whilk",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bwho\b"),
                    Box::new(DirectTarget { replacement: "wha" }),
                ),
                Replacement::new(
                    Source::Raw(r"\bwhole\b"),
                    Box::new(DirectTarget {
                        replacement: "hail",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bwhom\b"),
                    Box::new(DirectTarget {
                        replacement: "wham",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bwhose\b"),
                    Box::new(DirectTarget {
                        replacement: "wha`s",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bwife\b"),
                    Box::new(DirectTarget {
                        replacement: "guidwife",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bwives\b"),
                    Box::new(DirectTarget {
                        replacement: "guidwives",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bwind\b"),
                    Box::new(DirectTarget {
                        replacement: "win`",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bwindow\b"),
                    Box::new(DirectTarget {
                        replacement: "windae",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bwindows\b"),
                    Box::new(DirectTarget {
                        replacement: "windaes",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bwith\b"),
                    Box::new(DirectTarget { replacement: "wi`" }),
                ),
                Replacement::new(
                    Source::Raw(r"\bwithin\b"),
                    Box::new(DirectTarget {
                        replacement: "wi`in",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bwithout\b"),
                    Box::new(DirectTarget {
                        replacement: "wi`oot",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bwoman\b"),
                    Box::new(DirectTarget {
                        replacement: "wifie",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bwomen\b"),
                    Box::new(DirectTarget {
                        replacement: "Wummin",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bwork\b"),
                    Box::new(DirectTarget {
                        replacement: "wirk",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bwords\b"),
                    Box::new(DirectTarget {
                        replacement: "Wurds",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bworld\b"),
                    Box::new(DirectTarget {
                        replacement: "warl",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bworldly\b"),
                    Box::new(DirectTarget {
                        replacement: "war'ly",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bworking\b"),
                    Box::new(DirectTarget {
                        replacement: "wirkin",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bwould\b"),
                    Box::new(DirectTarget { replacement: "wid" }),
                ),
                Replacement::new(
                    Source::Raw(r"\bworse\b"),
                    Box::new(DirectTarget {
                        replacement: "waur",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bruined\b"),
                    Box::new(DirectTarget {
                        replacement: "clapped",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bwrong\b"),
                    Box::new(DirectTarget {
                        replacement: "wrang",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\byard\b"),
                    Box::new(DirectTarget {
                        replacement: "yaird",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\byeah\b"),
                    Box::new(DirectTarget { replacement: "aye" }),
                ),
                Replacement::new(
                    Source::Raw(r"\bTrue\b"),
                    Box::new(DirectTarget { replacement: "aye" }),
                ),
                Replacement::new(
                    Source::Raw(r"\byet\b"),
                    Box::new(DirectTarget { replacement: "yit" }),
                ),
                Replacement::new(
                    Source::Raw(r"\byou\b"),
                    Box::new(DirectTarget { replacement: "ye" }),
                ),
                Replacement::new(
                    Source::Raw(r"\byour\b"),
                    Box::new(DirectTarget { replacement: "yer" }),
                ),
                Replacement::new(
                    Source::Raw(r"\byoure\b"),
                    Box::new(DirectTarget {
                        replacement: "yer'r",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\byourself\b"),
                    Box::new(DirectTarget {
                        replacement: "yersel`",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bquiet\b"),
                    Box::new(DirectTarget {
                        replacement: "cannie",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bi\b"),
                    Box::new(DirectTarget { replacement: "a" }),
                ),
                Replacement::new(
                    Source::Raw(r"\bive\b"),
                    Box::new(DirectTarget {
                        replacement: "a've",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bim\b"),
                    Box::new(DirectTarget { replacement: "a'm" }),
                ),
                Replacement::new(
                    Source::Raw(r"\bit\b"),
                    Box::new(DirectTarget { replacement: "et" }),
                ),
                Replacement::new(
                    Source::Raw(r"\bshit\b"),
                    Box::new(DirectTarget {
                        replacement: "shite",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bshitsec\b"),
                    Box::new(DirectTarget {
                        replacement: "shitesec",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\balright\b"),
                    Box::new(DirectTarget {
                        replacement: "awricht",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bcrazy\b"),
                    Box::new(DirectTarget {
                        replacement: "doolally",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bidiot\b"),
                    Box::new(DirectTarget {
                        replacement: "eejit",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bidiots\b"),
                    Box::new(DirectTarget {
                        replacement: "eejits",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bugly\b"),
                    Box::new(DirectTarget {
                        replacement: "hackit",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\btired\b"),
                    Box::new(DirectTarget {
                        replacement: "knackert",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bgay\b"),
                    Box::new(DirectTarget {
                        replacement: "bufty",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\btesting\b"),
                    Box::new(DirectTarget {
                        replacement: "testin`",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bfuck\b"),
                    Box::new(DirectTarget {
                        replacement: "fook",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bfucking\b"),
                    Box::new(DirectTarget {
                        replacement: "fookin`,feckin",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bfucker\b"),
                    Box::new(DirectTarget {
                        replacement: "fooker",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bfuckers\b"),
                    Box::new(DirectTarget {
                        replacement: "fookers",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bmom\b"),
                    Box::new(DirectTarget { replacement: "maw" }),
                ),
                Replacement::new(
                    Source::Raw(r"\bmoms\b"),
                    Box::new(DirectTarget {
                        replacement: "maws",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bthrowing\b"),
                    Box::new(DirectTarget {
                        replacement: "chuckin",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bfucked\b"),
                    Box::new(DirectTarget {
                        replacement: "fooked",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bass\b"),
                    Box::new(DirectTarget {
                        replacement: "arse",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\basses\b"),
                    Box::new(DirectTarget {
                        replacement: "arses",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bbothered\b"),
                    Box::new(DirectTarget {
                        replacement: "arsed",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bdick\b"),
                    Box::new(DirectTarget {
                        replacement: "boaby",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bdicks\b"),
                    Box::new(DirectTarget {
                        replacement: "boabys",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bsomething\b"),
                    Box::new(DirectTarget {
                        replacement: "suhin",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bsomethings\b"),
                    Box::new(DirectTarget {
                        replacement: "suhins",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bboys\b"),
                    Box::new(DirectTarget {
                        replacement: "lads",
                    }),
                ),
                Replacement::new(
                    Source::Raw(r"\bgirls\b"),
                    Box::new(DirectTarget {
                        replacement: "lasses",
                    }),
                ),
            ],
        }
    }
}
