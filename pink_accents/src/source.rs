use std::convert::TryFrom;

/// Regex to match against.
pub enum Source {
    Raw(&'static str),
    Regex(fancy_regex::Regex),
}

impl TryFrom<Source> for fancy_regex::Regex {
    type Error = String;

    fn try_from(source: Source) -> Result<Self, Self::Error> {
        Ok(match source {
            Source::Raw(re) => fancy_regex::Regex::new(re)
                .map_err(|err| format!("regex compilation failed: {err}"))?,
            Source::Regex(regex) => regex,
        })
    }
}
