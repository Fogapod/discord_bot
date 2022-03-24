use std::collections::HashMap;
use std::fmt::Debug;

use rand::prelude::IteratorRandom;
use rand::prelude::SliceRandom;

use crate::capture::Capture;

pub trait Target: Debug + Send + Sync {
    fn callback<'text>(&self, m: Capture<'text>) -> &str;
}

#[derive(Debug)]
pub struct DirectTarget {
    pub replacement: &'static str,
}

impl<'text> Target for DirectTarget {
    fn callback(&self, _: Capture) -> &str {
        self.replacement
    }
}

impl<'text> Target for &str {
    fn callback(&self, _: Capture) -> &str {
        self
    }
}

impl<'text> Target for String {
    fn callback(&self, _: Capture) -> &str {
        self
    }
}

#[derive(Debug)]
pub struct MultiTarget {
    pub replacement: Vec<Box<dyn Target>>,
}

impl<'text> Target for MultiTarget {
    fn callback(&self, caps: Capture) -> &str {
        let selected = self.replacement.choose(&mut rand::thread_rng()).unwrap();

        selected.callback(caps)
    }
}

#[derive(Debug)]
pub struct MapTarget {
    pub replacement: HashMap<Box<dyn Target>, f32>,
}

impl<'text> Target for MapTarget {
    fn callback(&self, caps: Capture) -> &str {
        let selected = self
            .replacement
            .keys()
            .choose(&mut rand::thread_rng())
            .unwrap();

        selected.callback(caps)
    }
}
