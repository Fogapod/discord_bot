use std::borrow::Cow;

use crate::capture::Capture;
use crate::source::Source;
use crate::target::Target;

pub struct Replacement {
    source: fancy_regex::Regex,
    target: Box<dyn Target>,
}

impl Replacement {
    pub fn new(source: Source, target: Box<dyn Target>) -> Result<Self, String> {
        Ok(Self {
            source: source.try_into()?,
            target,
        })
    }

    pub fn apply<'text>(&self, text: &'text str, severity: i32) -> Cow<'text, str> {
        self.source
            .replace_all(text, |caps: &fancy_regex::Captures| {
                self.target.callback(Capture::new(caps, severity))
            })
    }
}
