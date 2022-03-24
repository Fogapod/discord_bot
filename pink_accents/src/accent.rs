use crate::replacement::Replacement;

pub trait Accent: Send + Sync {
    fn replacements(&self) -> &[Replacement];

    fn apply(&self, text: &str, severity: i32) -> String {
        self.replacements()
            .iter()
            .fold(text.to_string(), |acc, replacement| {
                replacement.apply(&acc, severity).into()
            })
    }
}
