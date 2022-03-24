use std::borrow::Cow;

use crate::capture::Capture;

pub enum Source {
    Raw(&'static str),
    Regex(fancy_regex::Regex),
}

pub trait Target {
    fn callback<'text>(&self, m: Capture<'text>) -> &str;
}

pub struct DirectTarget {
    pub replacement: &'static str,
}

impl<'text> Target for DirectTarget {
    fn callback(&self, _: Capture) -> &str {
        self.replacement
    }
}

pub struct Replacement {
    source: fancy_regex::Regex,
    target: Box<dyn Target + Sync + Send>,
}

impl Replacement {
    pub fn new(source: Source, target: Box<dyn Target + Sync + Send>) -> Self {
        let source_regex = match source {
            Source::Raw(s) => fancy_regex::Regex::new(s).unwrap(),
            Source::Regex(regex) => regex,
        };

        Self {
            source: source_regex,
            target,
        }
    }

    pub fn apply<'text>(&self, text: &'text str, severity: i32) -> Cow<'text, str> {
        self.source
            .replace_all(text, |caps: &fancy_regex::Captures| {
                self.target.callback(Capture::new(caps, severity))
            })
    }
}
