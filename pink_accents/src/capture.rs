#[derive(Debug)]
pub struct Capture<'text> {
    caps: &'text fancy_regex::Captures<'text>,
    severity: i32,
}

impl<'text> Capture<'text> {
    pub fn new(caps: &'text fancy_regex::Captures<'text>, severity: i32) -> Self {
        Self { caps, severity }
    }

    pub fn original(&self) -> &'text str {
        &self.caps[0]
    }
}
