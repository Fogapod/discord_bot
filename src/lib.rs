mod accent;
mod capture;
mod replacement;
mod scotsman;

use crate::accent::Accent;

use std::collections::HashMap;

use pyo3::prelude::*;

use lazy_static::lazy_static;
use parking_lot::RwLock;

lazy_static! {
    static ref ACCENTS: RwLock<HashMap<String, Box<dyn Accent>>> = RwLock::new(HashMap::new());
}

/// Apply accent to text. Looks up accent by name.
#[pyfunction]
fn apply_accent(accent: &str, text: &str, severity: i32) -> String {
    ACCENTS.read().get(accent).unwrap().apply(text, severity)
}

#[pymodule]
fn pink_accents_rs(_py: Python, m: &PyModule) -> PyResult<()> {
    ACCENTS
        .write()
        .insert("scotsman".to_string(), Box::new(scotsman::Scotsman::new()));

    m.add_function(wrap_pyfunction!(apply_accent, m)?)?;
    Ok(())
}
